// Run on an agent where we want to use Go
//node {
    // Ensure the desired Go version is installed
//    def root = tool type: 'go', name: 'Go 1.17'

    // Export environment variables pointing to the directory where Go was installed
//    withEnv(["GOROOT=${root}", "PATH+GO=${root}/bin"]) {
//        sh 'go version'
//        sh 'ls /var/lib/jenkins/workspace/'
//    }
//}
pipeline {
    stages {
    //checkout scm
    //stage('Checkout') {
    //    sh """
    //    git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    //    git fetch --all
    //    """
    //}

    //agent any
    //tools {
    //    go 'Go 1.17'
    //}
    //environment {
    //    GO111MODULE = 'on'
    //}
    //stages {
 
        stage('Release') {
            steps {
            agent {
                docker {
                    image 'Docker'
                    // Run the container on the node specified at the top-level of the Pipeline, in the same workspace, rather than on a new node entirely:
                    reuseNode true
                }
            }
            sh 'node --version'
            }
                //sh 'cd "/var/lib/jenkins/workspace/M7011E Github/"; nohup go run m7011e &'            
        }
    }
}
