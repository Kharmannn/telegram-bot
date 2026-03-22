pipeline {
    agent any

    environment {
        APP_DIR = '/opt/telegram-bot'
    }

    triggers {
        pollSCM('* * * * *')
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
                    mkdir -p ${APP_DIR}
                    cp -r ${WORKSPACE}/. ${APP_DIR}/
                    rm -rf ${APP_DIR}/.git ${APP_DIR}/credentials ${APP_DIR}/.env

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