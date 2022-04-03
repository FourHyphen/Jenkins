g_value1 = ''

pipeline {
    agent any

    stages {
        stage('Pre') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        pre_process()
                    }
                }
            }
        }
    }
}

def pre_process() {
    // 初期設定
    g_value1 = 'processed'
    println(g_value1)
}

return this
