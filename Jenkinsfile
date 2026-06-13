pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "shuja782"
        UNSTABLE_IMAGE = "shuja782/sentiment-api:unstable"
        STABLE_IMAGE   = "shuja782/sentiment-api:stable"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker rm -f sentiment-app || true
                    docker build -t sentiment-api:ci-unstable -f Dockerfile .
                    docker run -d --name sentiment-app -p 5000:5000 sentiment-api:ci-unstable

                    echo "Waiting for app to become healthy..."
                    for i in $(seq 1 30); do
                        if curl -sf http://localhost:5000/health > /dev/null; then
                            echo "App is up"
                            break
                        fi
                        sleep 5
                    done
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm --network host \
                        -v $WORKSPACE/tests:/app/tests \
                        sentiment-api:ci-unstable \
                        pytest /app/tests/test_api.py -v
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker build -t sentiment-ui-test -f Dockerfile.test .
                    docker run --rm --network host \
                        -v $WORKSPACE/tests:/tests \
                        sentiment-ui-test \
                        pytest /tests/test_ui.py -v
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        # Build and push unstable image
                        docker build -t $UNSTABLE_IMAGE -f Dockerfile .
                        docker push $UNSTABLE_IMAGE

                        # Build and push stable image from stable-fallback branch
                        rm -rf stable-branch
                        git clone -b stable-fallback https://github.com/shuja782/selfhealing-mlops-fa23-bai-040.git stable-branch
                        docker build -t $STABLE_IMAGE -f stable-branch/Dockerfile stable-branch
                        docker push $STABLE_IMAGE
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f sentiment-app || true'
        }
    }
}
