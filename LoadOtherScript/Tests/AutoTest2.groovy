import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

pipeline {
    agent any

    stages {
        stage('TestInit') {
            steps {
                // timestamper ver. 1.17
                // 1.18 以降なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        test_init(WORKSPACE)
                    }
                }
            }
        }

        stage('Clone') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        clone(REPOSITORY_URL, TEST_BRANCH, CREDENTIALS_ID, WORKSPACE)
                    }
                }
            }
        }

        stage('Execute') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        def date = LocalDateTime.now()
                        def now = date.format(DateTimeFormatter.ofPattern('yyyyMMdd_HHmmss'))
                        if (!execute_test_suite(WORKSPACE, "${now}_${BUILD_ID}")) {
                            error("test failed")
                        }
                    }
                }
            }
        }
    }

    post {
        // 失敗したときは環境確認のためにワークスペースをそのまま残す
        success {
            deleteDir()
        }
    }
}

def test_init(String workspace_path) {
    try {
        println(sh(returnStdout: true, script: "ls -l"))
    } catch (Exception e) {
        println(powershell(returnStdout: true, script: "dir ${workspace_path}"))
    }
}

def clone(String repositoryUrl, String branch, String credentialsId, String workspace_path) {
    dir(workspace_path) {
        clone_core(repositoryUrl, branch, credentialsId)
    }
}

def clone_core(String repositoryUrl, String branch, String credentialsId) {
    checkout([
        $class: 'GitSCM', 
        branches: [[name: "*/${branch}"]], 
        doGenerateSubmoduleConfigurations: false, 
        extensions: [[$class: 'CleanCheckout']], 
        submoduleCfg: [], 
        userRemoteConfigs: [[credentialsId: "${credentialsId}",
                             url: "${repositoryUrl}"]]
    ])
}

def execute_test_suite(String workspace_path, String unique_id) {
    def test_MainJobA = load("${workspace_path}/LoadOtherScript/Tests/test_MainJobA2.groovy")
    def common = load("${workspace_path}/LoadOtherScript/Tests/common.groovy")

    def result_test_MainJobA = test_MainJobA.test_suite(workspace_path, unique_id, common)

    if (result_test_MainJobA) {
        return true
    } else {
        return false
    }
}
