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
                    sh '''
                        set -euo pipefail

                        echo "🔐 Login to Infisical (Jenkins)..."

                        INFISICAL_TOKEN=$(infisical login \
                            --method=universal-auth \
                            --client-id="$INFISICAL_CLIENT_ID" \
                            --client-secret="$INFISICAL_CLIENT_SECRET" \
                            --domain="$INFISICAL_DOMAIN" \
                            --plain --silent)

                        echo "🌐 Fetch VPS config..."

                        VPS_HOST=$(infisical secrets get VPS_HOST --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain="$INFISICAL_DOMAIN" \
                            --token="$INFISICAL_TOKEN" --plain)

                        VPS_USER=$(infisical secrets get VPS_USER --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain="$INFISICAL_DOMAIN" \
                            --token="$INFISICAL_TOKEN" --plain)

                        echo "🚀 Connecting to $VPS_USER@$VPS_HOST..."

                        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
                        INFISICAL_CLIENT_ID="$INFISICAL_CLIENT_ID" \
                        INFISICAL_CLIENT_SECRET="$INFISICAL_CLIENT_SECRET" \
                        INFISICAL_DOMAIN="$INFISICAL_DOMAIN" \
                        'bash -s' << 'ENDSSH'

                        set -euo pipefail

                        echo "👤 USER: $(whoami)"
                        echo "🏠 HOME: $HOME"

                        BASE_DIR="$(eval echo ~$(whoami))/projects"
                        APP_DIR="$BASE_DIR/telegram-bot"

                        mkdir -p "$BASE_DIR"

                        if [ -d "$APP_DIR/.git" ]; then
                            echo "📥 Updating repo..."
                            cd "$APP_DIR"
                            git fetch origin
                            git reset --hard origin/main
                        else
                            echo "📦 Cloning repo..."
                            rm -rf "$APP_DIR"
                            git clone git@github.com:Kharmannn/telegram-bot.git "$APP_DIR"
                            cd "$APP_DIR"
                        fi

                        echo "🔐 Login to Infisical (VPS)..."

                        INFISICAL_TOKEN=$(infisical login \
                            --method=universal-auth \
                            --client-id="$INFISICAL_CLIENT_ID" \
                            --client-secret="$INFISICAL_CLIENT_SECRET" \
                            --domain="$INFISICAL_DOMAIN" \
                            --plain --silent)

                        export INFISICAL_TOKEN

                        echo "📄 Exporting secrets..."
                        infisical export \
                            --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain="$INFISICAL_DOMAIN" \
                            > .env

                        echo "🐳 Deploying with Docker..."
                        docker compose down || true
                        docker compose up -d --build

                        echo "🧹 Cleanup..."
                        rm -f .env

                        echo "✅ Deployment success!"

                        ENDSSH
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ expense-bot deployed successfully!'
        }
        failure {
            echo '❌ Deployment failed. Check logs.'
        }
    }
}