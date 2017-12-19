import sys 
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/icd_lstm/')
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/app/')
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/logic-lab/TextPreprocessing/')
from lstm_stack import lstm_stack

class icd_wrapper:
    def init(self):
        self.lstm = lstm_stack()
        self.lstm.load_models()

    def get_icd(self, document):
        codes = self.lstm.get_predictions(document)
        accuracy = 1
        code = ''
        for e in codes[:2]:
            code += e[0]
            accuracy *= float(e[1])
        return code + ":" + str(round(accuracy, 2))
    
    def get_icd_and_score(self, document):
        codes = self.lstm.get_predictions(document)
        accuracy = 1
        code = ''
        for e in codes[:2]:
            code += e[0]
            accuracy *= float(e[1])
        return code, str(round(accuracy, 2))