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
		sh 'cp -v dev.service ~/.config/systemd/user/'
		sh 'systemctl --user daemon-reload' 
		sh 'systemctl --user stop dev'
                sh 'systemctl --user start dev'
		sh 'systemctl --user status dev'
        }
    
}
