node {
    checkout scm
    stage('Checkout') {    
        sh """
        git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
        git fetch --all
        """
        
    }

    stage('build') {
	//sh 'mkdir ~/.config/systemd'
	//sh 'mkdir ~/.config/systemd/user'
	sh 'pip install mysql-connector'
    }   

    stage('Deploy') {
	sh 'cp -v flask.service ~/.config/systemd/user/'
	sh 'systemctl --user daemon-reload' 
	//sh 'systemctl --user stop flask'
        sh 'systemctl --user restart flask'
	sh 'systemctl --user status flask'
    }
    
}
