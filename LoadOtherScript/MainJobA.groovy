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
    g_value1 = 'processed'
    println(g_value1)
}
