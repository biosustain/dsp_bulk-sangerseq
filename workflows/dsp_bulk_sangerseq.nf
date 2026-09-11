include { PREPARE_INPUTS } from '../modules/local/prepare/inputs/main'
include { TRACY_DECOMPOSE } from '../modules/local/tracy/decompose/main'
include { TRACY_DECOMPOSE_POSTPROCESS } from '../modules/local/tracy/postprocess/main'
include { TRACY_ALIGN } from '../modules/local/tracy/align/main'
include { TRACY_ASSEMBLE } from '../modules/local/tracy/assemble/main'
include { TRACY_RENDER_VISUALISATIONS as TRACY_RENDER_ALIGN } from '../modules/local/tracy/render_visualisations/main'
include { TRACY_RENDER_VISUALISATIONS as TRACY_RENDER_DECOMPOSE } from '../modules/local/tracy/render_visualisations/main'
include { TRACY_RENDER_VISUALISATIONS as TRACY_RENDER_ASSEMBLE } from '../modules/local/tracy/render_visualisations/main'
include { TRACY_RENDER_VISUALISATIONS as TRACY_RENDER_ASSEMBLE_ALIGNMENT } from '../modules/local/tracy/render_visualisations/main'
include { VUEGEN_PREPARE_TREE } from '../modules/local/vuegen/prepare_tree/main'
include { VUEGEN } from '../modules/nf-core/vuegen/main'

workflow DSP_BULK_SANGERSEQ {
    def input_samplesheet = params.input ?: params.samplesheet

    if (!input_samplesheet) {
        error('Required parameter --samplesheet or --input was not provided')
    }

    if (!params.reference_fasta) {
        error('Required parameter --reference_fasta was not provided')
    }

    if (!params.data_dir) {
        error('Required parameter --data_dir was not provided')
    }

    def samplesheet_file = file(input_samplesheet)
    def reference_fasta_file = file(params.reference_fasta)
    def data_dir = file(params.data_dir)

    if (!samplesheet_file.exists()) {
        error("Samplesheet not found: ${input_samplesheet}")
    }

    if (!reference_fasta_file.exists()) {
        error("Reference FASTA not found: ${params.reference_fasta}")
    }

    if (!data_dir.exists()) {
        error("Data directory not found: ${params.data_dir}")
    }

    Channel.fromPath(input_samplesheet, checkIfExists: true).set { samplesheet_ch }
    Channel.fromPath(params.reference_fasta, checkIfExists: true).set { reference_fasta_ch }
    Channel.fromPath(params.data_dir, checkIfExists: true, type: 'dir').set { data_dir_ch }

    PREPARE_INPUTS(samplesheet_ch, reference_fasta_ch, data_dir_ch)

    def reference_ch = PREPARE_INPUTS.out.reference_files
        .flatten()
        .map { reference_file ->
            tuple(reference_file.baseName, reference_file)
        }

    def sample_tasks_ch = PREPARE_INPUTS.out.samples_tsv
    .splitCsv(header: true, sep: '\t')
    .combine(PREPARE_INPUTS.out.staged_data_dir)
    .map { row, staged_dir ->
        tuple(
            row.reference_id,
            row.sample_id,
            staged_dir.resolve(row.ab1_path),
        )
    }
    .combine(reference_ch, by: 0)
    .map { reference_id, sample_id, ab1_file, reference_file ->
        tuple(sample_id, ab1_file, reference_file)
    }
    .multiMap { item ->
        decompose: item
        align: item
    }
    .set { sample_branched }

    TRACY_DECOMPOSE(sample_branched.decompose)
    TRACY_ALIGN(sample_branched.align)

    TRACY_DECOMPOSE.out.json_results
        .map { sample_id, json_file -> json_file }
        .collect()
        .set { postprocess_ch }

    TRACY_DECOMPOSE_POSTPROCESS(postprocess_ch)

    def assembly_tasks_ch = PREPARE_INPUTS.out.assemblies_tsv
    .splitCsv(header: true, sep: '\t')
    .filter { row -> row.sample_id_joined?.trim() }
    .combine(PREPARE_INPUTS.out.staged_data_dir)
    .map { row, staged_dir ->
        def ab1_files = row.ab1_paths
            .split(';')
            .findAll { it }
            .collect { staged_dir.resolve(it) }

        tuple(
            row.reference_id,
            row.assembly_group,
            row.sample_id_joined,
            ab1_files,
        )
    }
    .combine(reference_ch, by: 0)
    .map { reference_id, assembly_group, sample_id_joined, ab1_files, reference_file ->
        tuple(assembly_group, sample_id_joined, reference_file, ab1_files)
    }

    TRACY_ASSEMBLE(assembly_tasks_ch)

    TRACY_ALIGN.out.json_results
        .map { sample_id, json_file -> tuple(sample_id, 'align', json_file) }
        .set { align_viewer_ch }
    TRACY_RENDER_ALIGN(align_viewer_ch)

    TRACY_DECOMPOSE.out.json_results
        .map { sample_id, json_file -> tuple(sample_id, 'decompose', json_file) }
        .set { decompose_viewer_ch }

    TRACY_RENDER_DECOMPOSE(decompose_viewer_ch)

    // tracy assemble writes two things worth looking at, so the group gets two
    // viewers. The JSON carries the aligned traces and the consensus the Pearl
    // viewer draws; the `.align.fa` is the gapped multi-FASTA of the reads
    // against the reference, which Sabre draws read by read. Pearl does not
    // show that - it colour-codes a single consensus line from the same
    // alignment - so the two viewers complement rather than repeat each other.
    def assemble_files_ch = TRACY_ASSEMBLE.out.assemble_results
        .flatMap { _group, files -> (files instanceof List) ? files : [files] }

    // The assembly group's joined sample id is taken from the output's own
    // name, so the viewers are named like the rest of the group's outputs.
    assemble_files_ch
        .filter { assemble_file -> assemble_file.name.endsWith('.json') }
        .map { json_file -> tuple(json_file.baseName, 'assemble', json_file) }
        .set { assemble_viewer_ch }

    assemble_files_ch
        .filter { assemble_file -> assemble_file.name.endsWith('.align.fa') }
        .map { align_fasta ->
            def group_name = align_fasta.name - '.align.fa'
            tuple("${group_name}_alignment", 'assemble', align_fasta)
        }
        .set { assemble_alignment_viewer_ch }

    TRACY_RENDER_ASSEMBLE(assemble_viewer_ch)
    TRACY_RENDER_ASSEMBLE_ALIGNMENT(assemble_alignment_viewer_ch)

    // Assemble the VueGen report from the per-section tracy outputs. Each
    // upstream channel is filtered down to just the files that section needs
    // and collected so the report is built once from all samples.
    //
    // Every section carries the rendered viewer rather than tracy's text
    // reports: the Indigo viewer already shows the `.align1` / `.align2` /
    // `.align3` alignments, the Sage viewer the align step's `.txt` alignment,
    // and the assembly's two viewers its `.json` traces and `.align.fa`
    // alignment. All of those text outputs stay published under `outdir/`.
    def decompose_viewer_report_ch = TRACY_RENDER_DECOMPOSE.out.html_viewer
        .map { _section, html_file -> html_file }
        .collect()
        .ifEmpty([])

    def align_viewer_report_ch = TRACY_RENDER_ALIGN.out.html_viewer
        .map { _section, html_file -> html_file }
        .collect()
        .ifEmpty([])

    // Both assembly viewers go into the same section: their file names differ
    // (`<group>.html` for Pearl, `<group>_alignment.html` for Sabre), so they
    // sit side by side without colliding.
    def assemble_viewer_report_ch = TRACY_RENDER_ASSEMBLE.out.html_viewer
        .mix(TRACY_RENDER_ASSEMBLE_ALIGNMENT.out.html_viewer)
        .map { _section, html_file -> html_file }
        .collect()
        .ifEmpty([])

    VUEGEN_PREPARE_TREE(
        TRACY_DECOMPOSE_POSTPROCESS.out.combined,
        decompose_viewer_report_ch,
        align_viewer_report_ch,
        assemble_viewer_report_ch,
    )

    VUEGEN(
        Channel.value('directory'),
        VUEGEN_PREPARE_TREE.out.tree,
        Channel.value(params.vuegen_report_type),
    )
}
