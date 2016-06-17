class DataRecorder:

  def __init__(self,output_file_name):
    self._outputFileName = output_file_name
    self._dataRecord = {}

  def captureData(self,data,record_name='default'):
    try:
      if record_name not in self._dataRecord:
        self._dataRecord[record_name] = pd.DataFrame(columns=data.keys())
      self._dataRecord[record_name] = self._dataRecord[record_name].append(data,ignore_index=True)
    except:
      if record_name not in self._dataRecord:
        self._dataRecord[record_name] = {'columns':data.keys(),'data_rows':[]}
      self._dataRecord[record_name]['data_rows'].append(['{v:0.5f}'.format(v=v) for v in data.values()])

  def getDataRecord(self,record_name='default'):
    return self._dataRecord[record_name]

  def saveDataRecord(self,record_name='default'):
    self._dataRecord[record_name].to_csv(self._outputFileName,index=False)
