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
node {
    //agent any
    //tools {
    //    go 'Go 1.17'
    //}
    //environment {
    //    GO111MODULE = 'on'
    //}
    //stages {
        //stage('Compile'){
          //  steps {
            //    sh 'cd "/var/lib/jenkins/workspace/M7011E Github/"; go build .'
            //}
        //}
        stage('Release') {
          
                //sh 'cd "/var/lib/jenkins/workspace/M7011E Github/"; nohup go run m7011e &' 
            sh 'ls'
            
        }
    //}
}
