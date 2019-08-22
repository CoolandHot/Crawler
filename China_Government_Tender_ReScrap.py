from China_Government_Tender import writeInfile
import os

if __name__=="__main__":
    error_basic_path="Error_URL_"
    for i in range(5):
        error_f_path=error_basic_path+str(i)+".txt"
        if os.path.exists(error_f_path):
            continue
        else:
            break
    read_f_path=error_basic_path+str(i-1)+".txt"
    writeInfile(read_f_path,error_f_path)
    print("错误链接补全完毕")