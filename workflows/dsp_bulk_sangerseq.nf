include { PREPARE_INPUTS } from '../modules/local/prepare/inputs/main'
include { TRACY_DECOMPOSE } from '../modules/local/tracy/decompose/main'
include { TRACY_POSTPROCESS } from '../modules/local/tracy/postprocess/main'
include { TRACY_ALIGN } from '../modules/local/tracy/align/main'
include { TRACY_ASSEMBLE } from '../modules/local/tracy/assemble/main'
include { COPY_TRACE_JS } from '../modules/local/utils/copy_trace_js/main'
include { RENDER_ALIGN_VIEWER } from '../modules/local/utils/render_align_viewer/main'

workflow DSP_BULK_SANGERSEQ {
    def input_samplesheet = params.input ?: params.samplesheet

    if (!input_samplesheet) {
        error 'Required parameter --samplesheet or --input was not provided'
    }

    if (!params.reference_fasta) {
        error 'Required parameter --reference_fasta was not provided'
    }

    if (!params.data_dir) {
        error 'Required parameter --data_dir was not provided'
    }

    def samplesheet_file = file(input_samplesheet)
    def reference_fasta_file = file(params.reference_fasta)
    def data_dir = file(params.data_dir)

    if (!samplesheet_file.exists()) {
        error "Samplesheet not found: ${input_samplesheet}"
    }

    if (!reference_fasta_file.exists()) {
        error "Reference FASTA not found: ${params.reference_fasta}"
    }

    if (!data_dir.exists()) {
        error "Data directory not found: ${params.data_dir}"
    }

    Channel.fromPath(input_samplesheet, checkIfExists: true).set { samplesheet_ch }
    Channel.fromPath(params.reference_fasta, checkIfExists: true).set { reference_fasta_ch }
    Channel.fromPath("${projectDir}/static/traceView.js", checkIfExists: true).set { trace_js_ch }

    PREPARE_INPUTS(samplesheet_ch, reference_fasta_ch)

    def reference_ch = PREPARE_INPUTS.out.reference_files
        .flatten()
        .map { reference_file ->
            tuple(reference_file.baseName, reference_file)
        }

    def sample_tasks_ch = PREPARE_INPUTS.out.samples_tsv
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            tuple(
                row.reference_id,
                row.sample_id,
                file(row.ab1_path, checkIfExists: true)
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

    TRACY_POSTPROCESS(postprocess_ch)

    def assembly_tasks_ch = PREPARE_INPUTS.out.assemblies_tsv
        .splitCsv(header: true, sep: '\t')
        .filter { row -> row.sample_id_joined?.trim() }
        .map { row ->
            def ab1_files = row.ab1_paths
                .split(';')
                .findAll { it }
                .collect { file(it, checkIfExists: true) }

            tuple(
                row.reference_id,
                row.assembly_group,
                row.sample_id_joined,
                ab1_files
            )
        }
        .join(reference_ch)
        .map { reference_id, assembly_group, sample_id_joined, ab1_files, reference_file ->
            tuple(assembly_group, sample_id_joined, reference_file, ab1_files)
        }

    TRACY_ASSEMBLE(assembly_tasks_ch)
    COPY_TRACE_JS(trace_js_ch)

    TRACY_ALIGN.out.json_results
        .combine(trace_js_ch)
        .map { sample_id, json_file, trace_js_file ->
            tuple(sample_id, json_file, trace_js_file)
        }
        .set { viewer_tasks_ch }

    RENDER_ALIGN_VIEWER(viewer_tasks_ch)
}
