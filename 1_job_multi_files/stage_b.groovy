// import utilities.PreProcess    // 別ファイルに package utilities を定義する方法では unable to resolve class utilities.PreProcess
// export CLASSPATH="1_job_multi_files"    // これでも PreProcess 参照不可

// 事前条件: 前もって ProcessType を参照可能にすること
def stage_b(def jenkins_job, ProcessType process_type) {
    println("stage_b.groovy: stage_b()")

    StringBuilder builder = new StringBuilder()

    // 他ファイル定義のクラスを直接参照する手段がない(ClassLoader を使用するにも File クラスは許可が必要なので使えない)
    String pre_process_path = "1_job_multi_files/pre_process"
    def pre_process = load("${pre_process_path}/factory.groovy").create(jenkins_job, pre_process_path, ProcessType.Emulation)

    builder.append(create_header())
    builder.append(pre_process.create_process())

    println(builder.toString())
}

String create_header() {
    return """/bin/bash
"""
}

return this
