pipeline {
    agent any

    stages {
        stage('Hello') {
            steps {
                echo 'job_b'
            }
        }
    }
}
