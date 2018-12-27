import threading
import extract_api_pg
import os

#github_api.extract_all_issue

# if __name__ == "__main__":
    
#     t1 = threading.Thread(target=github_api.extract,args=(51,200),name="t_1")
#     # t2 = threading.Thread(target=github_api.extract,args=(800,1000),name="t_2")
#     # t3 = threading.Thread(target=github_api.extract,args=(1200,1400),name="t_3")
#     # t4 = threading.Thread(target=github_api.extract,args=(1400,1600),name="t_4")
#     # threading.Thread(target=github_api.extract_all_issue,args=(800,800),name="t_")

#     t1.start()
#     # t2.start()
#     # t3.start()
#     # t4.start()

#     t1.join()
#     # t2.join()
#     # t3.join()
#     # t4.join()


links = ["https://github.com/kubernetes/kubernetes/issues/60814","https://github.com/kubernetes/kubernetes/issues/60814"]

if __name__ == "__main__":
    
    t1 = threading.Thread(target=extract_api_pg.extract,args=(links),name="t_1")
    # t2 = threading.Thread(target=github_api.extract,args=(800,1000),name="t_2")
    # t3 = threading.Thread(target=github_api.extract,args=(1200,1400),name="t_3")
    # t4 = threading.Thread(target=github_api.extract,args=(1400,1600),name="t_4")
    # threading.Thread(target=github_api.extract_all_issue,args=(800,800),name="t_")

    t1.start()
    # t2.start()
    # t3.start()
    # t4.start()

    t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
