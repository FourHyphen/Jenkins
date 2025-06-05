g_value1 = ''

pipeline {
    agent any

    stages {
        stage('Pre') {
            steps {
                timestamps {
                    script {
                        pre_process()
                    }
                }
            }
        }

        stage('Stage A') {
            steps {
                timestamps {
                    script {
                        stage_a()
                    }
                }
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}

def pre_process() {
    deleteDir()

    // withCredentials(
    //     [usernamePassword(credentialsId: 'github.com_Jenkins_repository', usernameVariable: 'USER_GIT',passwordVariable: 'PASSWORD_GIT')]
    // ) { }
    checkout([$class: 'GitSCM',
        branches: [[name: '*/main']],
        doGenerateSubmoduleConfigurations: false,
        extensions: [], 
        submoduleCfg: [], 
        userRemoteConfigs: [[credentialsId: 'github.com_Jenkins_repository', url: GIT_REPOSITORY_URL]]
    ])

    sh('ls -l')
}

def stage_a() {
    println("stage_a()")
    sh('find ./ -type f')

    jenkinsfile = load("1_job_multi_files/stage_a.groovy")
    def data_a = new jenkinsfile.DataA()
    data_a.name = "Tsumugi"
    data_a.age = 17

    jenkinsfile.stage_a(data_a)
}
