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
                    string(credentialsId: 'infisical-client-secret', variable: 'INFISICAL_CLIENT_SECRET')
                ]) {
                    sh """
                        ssh ubuntu@43.156.57.193 '
                            cd /opt/expense-bot && \
                            git pull origin main && \
                            INFISICAL_TOKEN=\$(infisical login \
                                --method=universal-auth \
                                --client-id=${INFISICAL_CLIENT_ID} \
                                --client-secret=${INFISICAL_CLIENT_SECRET} \
                                --domain=https://geheim.kharmannn.my.id \
                                --plain --silent) && \
                            infisical run --env=production \
                                --projectId=3a3eab5c-0d3b-40e1-967d-23c7bd128670 \
                                --domain=https://geheim.kharmannn.my.id \
                                --token=\$INFISICAL_TOKEN \
                                -- docker compose up -d --build
                        '
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