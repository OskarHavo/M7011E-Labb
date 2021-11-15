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
		sh 'cp -v users.service ~/.config/systemd/user/'
		sh 'systemctl --user daemon-reload' 
		sh 'systemctl --user stop users'
                sh 'systemctl --user start users'
		sh 'systemctl --user status users'
        }
    
}
