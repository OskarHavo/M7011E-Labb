node {
    checkout scm
    stage('Checkout') {    
        sh """
        git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
        git fetch --all
        """
        
    }
    stage('Build') { 
        
        sh 'go build .' 
        
    }

        stage('Deploy') {
		sh 'cp -v logic.service ~/.config/systemd/user/'
		sh 'systemctl --user daemon-reload' 
		sh 'systemctl --user stop logic'
                sh 'systemctl --user start logic'
		sh 'systemctl --user status logic'
        }
    
}
