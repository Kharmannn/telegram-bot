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
                        set -e

                        # 🔐 Login to Infisical (Jenkins)
                        INFISICAL_TOKEN=\$(infisical login \
                            --method=universal-auth \
                            --client-id=\$INFISICAL_CLIENT_ID \
                            --client-secret=\$INFISICAL_CLIENT_SECRET \
                            --domain=\$INFISICAL_DOMAIN \
                            --plain --silent)

                        # 🌐 Get VPS info
                        VPS_HOST=\$(infisical secrets get VPS_HOST --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain=\$INFISICAL_DOMAIN \
                            --token=\$INFISICAL_TOKEN --plain)

                        VPS_USER=\$(infisical secrets get VPS_USER --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain=\$INFISICAL_DOMAIN \
                            --token=\$INFISICAL_TOKEN --plain)

                        echo "🚀 Connecting to VPS..."

                        ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$VPS_USER@\$VPS_HOST \\
                        "INFISICAL_CLIENT_ID='\$INFISICAL_CLIENT_ID' \\
                         INFISICAL_CLIENT_SECRET='\$INFISICAL_CLIENT_SECRET' \\
                         INFISICAL_DOMAIN='\$INFISICAL_DOMAIN' \\
                         bash -s" << ENDSSH

                            set -e

                            echo "👤 USER: \$USER"
                            echo "🏠 HOME: \$HOME"

                            # ✅ FIX: use HOME instead of USER
                            APP_DIR="\$HOME/projects/telegram-bot"

                            echo "📁 App directory: \$APP_DIR"

                            mkdir -p "\$HOME/projects"

                            # ✅ CLEAN repo sync
                            if [ -d "\$APP_DIR/.git" ]; then
                                echo "📥 Syncing repository..."
                                cd "\$APP_DIR"
                                git fetch origin
                                git reset --hard origin/main
                            else
                                echo "📦 Cloning repository..."
                                rm -rf "\$APP_DIR"
                                git clone git@github.com:Kharmannn/telegram-bot.git "\$APP_DIR"
                                cd "\$APP_DIR"
                            fi

                            # 🔐 Login to Infisical (VPS)
                            INFISICAL_TOKEN=\$(infisical login \
                                --method=universal-auth \
                                --client-id="\$INFISICAL_CLIENT_ID" \
                                --client-secret="\$INFISICAL_CLIENT_SECRET" \
                                --domain="\$INFISICAL_DOMAIN" \
                                --plain --silent)

                            export INFISICAL_TOKEN="\$INFISICAL_TOKEN"

                            echo "🔐 Exporting secrets..."

                            # ✅ use export (clean)
                            infisical export \
                                --env=prod \
                                --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                                --domain="\$INFISICAL_DOMAIN" \
                                > .env

                            echo "🐳 Running Docker..."

                            docker compose up -d --build

                            # ✅ fix permissions (important)
                            sudo chown -R \$USER:\$USER "\$APP_DIR"

                            echo "🧹 Cleaning .env..."
                            rm -f .env

                            echo "✅ Deployment finished!"

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