// Factory メソッド
def create(def jenkins_job, String pre_process_path, ProcessType process_type) {
    if (process_type == ProcessType.Emulation) {
        emulation = load("${pre_process_path}/emulation.groovy")
        return emulation.create_instance(jenkins_job)
    } else if (process_type == ProcessType.OnBoard) {
        on_board = load("${pre_process_path}/on_board.groovy")
        return on_board.create_instance(jenkins_job)
    }

    jenkins_job.error("PreProcess.Factory: not implementation exception(ProcessType: ${process_type}).")
}

return this
