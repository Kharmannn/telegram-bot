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
                withCredentials([
                    string(credentialsId: 'infisical-client-id', variable: 'INFISICAL_CLIENT_ID'),
                    string(credentialsId: 'infisical-client-secret', variable: 'INFISICAL_CLIENT_SECRET')
                ]) {
                    sh """
                        mkdir -p ${APP_DIR}
                        cp -r ${WORKSPACE}/. ${APP_DIR}/
                        rm -rf ${APP_DIR}/.git ${APP_DIR}/credentials ${APP_DIR}/.env

                        cd ${APP_DIR}
                        INFISICAL_TOKEN=\$(infisical login \
                            --method=universal-auth \
                            --client-id=\$INFISICAL_CLIENT_ID \
                            --client-secret=\$INFISICAL_CLIENT_SECRET \
                            --domain=https://geheim.kharmannn.my.id \
                            --plain --silent)

                        infisical run --env=prod \
                            --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                            --domain=https://geheim.kharmannn.my.id \
                            --token=\$INFISICAL_TOKEN \
                            -- docker-compose up -d --build
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