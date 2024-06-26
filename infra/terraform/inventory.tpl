[ec2_instances]
%{ for index, ip in instances }
host${index} ansible_host=${ip} input_file=/home/vishwajeet/projects/job_parser/postings_parser/input/urls_batch_${index}.txt
%{ endfor }
