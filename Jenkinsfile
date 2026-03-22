pipeline {
    agent any

    environment {
        APP_DIR = '/opt/expense-bot'
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
                withCredentials([infisicalSecret(credentialsId: 'infisical-jenkins',
                    projectSlug: 'telegram-bot',
                    envSlug: 'prod')]) {
                    sh """
                        mkdir -p ${APP_DIR}
                        cp -r ${WORKSPACE}/. ${APP_DIR}/
                        rm -rf ${APP_DIR}/.git ${APP_DIR}/credentials ${APP_DIR}/.env

                        cd ${APP_DIR}
                        docker compose up -d --build
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