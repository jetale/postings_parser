[ec2_instances]
%{ for ip in instances }
${ip}
%{ endfor }
