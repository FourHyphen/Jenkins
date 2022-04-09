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

        stage('Clone') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        clone_fake(g_value1)
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

def clone_fake(String value) {
    println("start clone(fake).")
    println("${value}")
    println("finish clone(fake).")
}
