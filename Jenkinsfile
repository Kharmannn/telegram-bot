pipeline {
    agent any

    environment {
        APP_DIR = '/opt/expense-bot'
        COMPOSE_FILE = 'docker-compose.yml'
    }

    triggers {
        pollSCM('* * * * *')  // check every minute
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy') {
            steps {
                sh """
                    # Sync code ke app directory
                    rsync -av --exclude='.git' \
                        --exclude='credentials/' \
                        --exclude='.env' \
                        ${WORKSPACE}/ ${APP_DIR}/

                    # Masuk ke app directory dan jalankan
                    cd ${APP_DIR}
                    infisical run --env=prod -- docker compose up -d --build
                """
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