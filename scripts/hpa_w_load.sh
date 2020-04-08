CONTROLLER=/local/repository/hpa_controller
cd $CONTROLLER

kubectl deploy -f deploy-w-load

sudo apt install -y at

echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance10.yaml" | at now + 30 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance9.yaml" | at now + 60 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance8.yaml" | at now + 90 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance7.yaml" | at now + 120 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance6.yaml" | at now + 150 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance5.yaml" | at now + 180 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance4.yaml" | at now + 210 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance3.yaml" | at now + 240 minutes
echo "kubectl delete -f ${CONTROLLER}/deploy-w-load/instance2.yaml" | at now + 270 minutes
POD_NAME=$(kubectl get pods | grep cpu-control1 | head -1 |  cut -d' ' -f1)
echo "kubectl cp $POD_NAME:/data/temp.db instance1.db" | at now + 300 minutes
