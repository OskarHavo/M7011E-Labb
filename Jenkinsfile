pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps{
        sh """
        git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
        git fetch --all
        """
            }
    }
    stage('Build') { 
        steps {
        sh 'go build .' 
        }
    }

        stage('Deploy') {
            steps {
                sh 'go run m7011e'
            }
        }
    }
}
