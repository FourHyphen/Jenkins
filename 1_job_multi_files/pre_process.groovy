import groovy.json.*

// enum ProcessType 参照
load("1_job_multi_files/stage_b.groovy")

// cps 変換のためにシリアライズ化が必要
// 本当は interface で String create_process() を強制したかったが他ファイルを load してもクラスは使えなかった
class PreProcess implements Serializable {
    def jenkins_job = null    // 呼び出し元 Jenkins ジョブ環境
    ProcessType process_type = ProcessType.Emulation 

    // groovy のセッタ機能を使用して Read Only 化(groovy はメンバ定義に private をつけても public になる)
    def setJenkins_job(def jenkins_job) {
        jenkins_job.error('ProcessBuilder: "jenkins_job" property is read-only')
    }

    def setProcess_type(ProcessType process_type) {
        jenkins_job.error('ProcessBuilder: "process_type" property is read-only')
    }

    // コンストラクタ
    def PreProcess(def jenkins_job, ProcessType process_type) {
        this.jenkins_job = jenkins_job
        this.process_type = process_type
    }

    String create_process() {
        builder.append("in PreProcess")
    }
}

PreProcess create(def jenkins_job, ProcessType process_type) {
    return new PreProcess(jenkins_job, process_type)
}

return this
