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
           
	    	sh 'mkdir -p  ~/.config/systemd/user/'
		//sh 'sudo cp app.service /etc/systemd/system/'
		sh 'cp -v app.service ~/.config/systemd/user'
		
		//sh 'echo "starting app..."'
		sh 'systemctl --user stop app'
		sh 'systemctl --user daemon-reload'
                sh 'systemctl --user start app'
		sh 'systemctl --user status app'
		//sh 'echo "script finished"'	
        }
    
}
