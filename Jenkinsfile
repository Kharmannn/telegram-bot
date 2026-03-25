pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    string(credentialsId: 'infisical-client-id', variable: 'INFISICAL_CLIENT_ID'),
                    string(credentialsId: 'infisical-client-secret', variable: 'INFISICAL_CLIENT_SECRET'),
                    string(credentialsId: 'infisical-domain', variable: 'INFISICAL_DOMAIN'),
                    sshUserPrivateKey(credentialsId: 'vps-ssh-key', keyFileVariable: 'SSH_KEY')
                ]) {
                    sh """
                        INFISICAL_TOKEN=\$(infisical login \
                            --method=universal-auth \
                            --client-id=\$INFISICAL_CLIENT_ID \
                            --client-secret=\$INFISICAL_CLIENT_SECRET \
                            --domain=\$INFISICAL_DOMAIN \
                            --plain --silent)

                        VPS_HOST=\$(infisical secrets get VPS_HOST --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain=\$INFISICAL_DOMAIN \
                            --token=\$INFISICAL_TOKEN --plain)

                        VPS_USER=\$(infisical secrets get VPS_USER --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain=\$INFISICAL_DOMAIN \
                            --token=\$INFISICAL_TOKEN --plain)

                        ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$VPS_USER@\$VPS_HOST << ENDSSH
                            set -e
                            APP_DIR=\$HOME/projects/telegram-bot

                            if [ -d "\$APP_DIR/.git" ]; then
                                echo "Pulling..."
                                cd \$APP_DIR && git pull origin main
                            else
                                echo "Cloning..."
                                mkdir -p \$HOME/projects
                                rm -rf \$APP_DIR
                                git clone git@github.com:Kharmannn/telegram-bot.git \$APP_DIR
                            fi

                            cd \$APP_DIR

                            INFISICAL_TOKEN=\$(infisical login \
                                --method=universal-auth \
                                --client-id=$INFISICAL_CLIENT_ID \
                                --client-secret=$INFISICAL_CLIENT_SECRET \
                                --domain=$INFISICAL_DOMAIN \
                                --plain --silent)

                            export INFISICAL_TOKEN=$INFISICAL_TOKEN

                            infisical export \
                                --env=prod \
                                --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                                --domain=$INFISICAL_DOMAIN \
                                > .env

                            docker compose up -d --build
                            rm -f .env
ENDSSH
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ expense-bot deployed successfully!'
        }
        failure {
            echo '❌ Deployment failed. Check logs above.'
        }
    }
}