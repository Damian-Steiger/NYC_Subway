
import glob
import pandas as pd
#import pandas as pd

#keep_col = ["1340387.42164835","1154650.28257997","-6107288.69629738"]
#two = [1340403.90416034,1154667.24721387,-6107282.06118808]
#three = [1341174.34669272,1155551.82007539,-6106968.12651604]
#four = [1341222.7509102,1155574.8171849,-6106951.3412304]
#five = [1344756.43390164,1158583.34985457,-6105620.98315242]
#keep_col = [one, two, three, four, five]
#for x in range (1, 5):
#    print(x)
#    f=pd.read_csv(str(x)+".csv")
#    new_f = f[keep_col[x]]
#    new_f.to_csv("newFile.csv", index=False)
#
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
