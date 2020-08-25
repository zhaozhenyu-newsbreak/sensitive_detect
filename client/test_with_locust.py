from locust import HttpUser, task, between
import json
import os
def load_file(path):
    res = []
    for lines in open(path):
        res.append(json.loads(lines.strip()))
    return res

class Test(HttpUser):
    file_data = load_file('../../../notAdultDeduped.data')

   
    @task
    def test_from_file(self):
        for data in self.file_data:
            self.client.post('/api/v0/sensitive',json = data)

if __name__=='__main__':
    os.system("locust -f test_with_locust.py --host=https://0.0.0.0:9111")
