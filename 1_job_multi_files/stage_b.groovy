// import utilities.PreProcess    // 別ファイルに package utilities を定義する方法では unable to resolve class utilities.PreProcess
// import pre_process    // unable to resolve class pre_process
// export CLASSPATH="1_job_multi_files"    // これでも PreProcess 参照不可

enum ProcessType {
    Emulation,
    OnBoard
}

// ただ load するだけだと参照不可。enum を load 先で参照する仕掛け
//  -> このファイルを複数 load されると 2 重定義エラーになるので注意が必要
this.ProcessType = ProcessType

def stage_b(def jenkins_job, ProcessType process_type) {
    println("stage_b.groovy: stage_b()")

    StringBuilder builder = new StringBuilder()

    // 他ファイル定義のクラスを直接参照する手段がない(ClassLoader を使用するにも File クラスは許可が必要なので使えない)
    pre_process = load("1_job_multi_files/pre_process.groovy")
    def pre_process = pre_process.create(jenkins_job, ProcessType.Emulation)

    builder.append(create_header())
    builder.append(pre_process.create_process())

    println(builder.toString())
}

String create_header() {
    return """/bin/bash
"""
}

return this
