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

void stage_a() {
    println("stage_a()")
    sh('find ./ -type f')

    jenkinsfile = load("1_job_multi_files/stage_a.groovy")
    def input_json = jenkinsfile.create_input_json(this, "Tsumugi", 17)
    try {
        input_json.name = "Mizuki"
        println("InputJson.name can read and write: writing \"${input_json.name}\"")
    } catch(Exception e) {
        println(e.toString())
        println("InputJson.name is read only.")
    }

    jenkinsfile.stage_a(input_json)
}
