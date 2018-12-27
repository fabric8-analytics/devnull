import threading
import github_api
import os

#github_api.extract_all_issue

if __name__ == "__main__":
    
    t1 = threading.Thread(target=github_api.extract,args=(0,1),name="t_1")
#    t2 = threading.Thread(target=github_api.extract,args=(310,340),name="t_2")
#    t3 = threading.Thread(target=github_api.extract,args=(340,360),name="t_3")
#    t4 = threading.Thread(target=github_api.extract,args=(360,380),name="t_4")
#    t5 = threading.Thread(target=github_api.extract,args=(380,400),name="t_5")

    t1.start()
#    t2.start()
#    t3.start()
#    t4.start()
#    t5.start()

    t1.join()
#    t2.join()
#    t3.join()
#    t4.join()
#    t5.join()
