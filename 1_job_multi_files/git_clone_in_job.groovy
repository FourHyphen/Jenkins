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

        stage('Stage B') {
            steps {
                timestamps {
                    script {
                        stage_b()
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

void stage_b() {
    println("stage_b(): start")

    // 準備
    // load ファイル定義の enum を使用するには少し工夫が必要(process_type.groovy 参照)
    load("1_job_multi_files/process_type.groovy")
    def process_type = ProcessType.Emulation

    // 本体処理呼び出し
    withCredentials(
        [usernamePassword(credentialsId: 'credentials_test', usernameVariable: 'USER_CREDENTIALS',passwordVariable: 'PASSWORD_CREDENTIALS')]
    ) {
        // この先のクラス内でクレデンシャルを参照する方法
        // クレデンシャル含む文字列を StringBuilder.append() しても withCredentials 内ならちゃんと隠してくれる
        // NG: "USER_CREDENTIALS: ${USER_CREDENTIALS}"
        // OK: "USER_CREDENTIALS: ${jenkins_job.USER_CREDENTIALS}"
        load("1_job_multi_files/stage_b.groovy").stage_b(this, process_type)
    }

    // 終了
    println("stage_b(): finish")
}
