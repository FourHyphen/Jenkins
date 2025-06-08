import groovy.json.*

// cps 変換のためにシリアライズ化が必要
// 本当は interface で String create_process() を強制したかったが他ファイルを load してもクラスは使えなかった
class PreProcessEmulation implements Serializable {
    def jenkins_job = null    // 呼び出し元 Jenkins ジョブ環境

    // groovy のセッタ機能を使用して Read Only 化(groovy はメンバ定義に private をつけても public になる)
    def setJenkins_job(def jenkins_job) {
        jenkins_job.error('ProcessBuilder: "jenkins_job" property is read-only')
    }

    // コンストラクタ
    def PreProcessEmulation(def jenkins_job) {
        this.jenkins_job = jenkins_job
    }

    String create_process() {
        return "echo \"PreProcessEmulation.create_process()\""
    }
}

PreProcessEmulation create_instance(def jenkins_job) {
    return new PreProcessEmulation(jenkins_job)
}

return this
