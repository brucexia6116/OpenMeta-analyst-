#################################################################
#
#  Byron C. Wallace
#  Tufts Medical Center
#  OpenMeta[analyst]
#  ---
#  Proxy interfaces for mediating between the underlying representation (in ma_dataset.py)
#  and the editing UI.
################################################################

#import pdb

# core libraries
#from PyQt4.QtCore import *
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, QString, Qt, QVariant

class TXGroupsModel(QAbstractTableModel):
    '''
    This module mediates between the classes comprising a dataset
    (i.e., study & ma_unit objects) and the view. In particular, we
    subclass the QAbstractTableModel and provide the fields of interest
    to the view.
    '''
    def __init__(self, filename=QString(), dataset=None, outcome=None, follow_up=None):
        super(TXGroupsModel, self).__init__()
        self.dataset = dataset
        self.current_outcome = outcome
        self.current_follow_up = follow_up
        self.refresh_group_list(outcome, follow_up)
        
    def refresh_group_list(self, outcome, follow_up):
        self.group_list = self.dataset.get_group_names_for_outcome_fu(outcome, follow_up)
        print "\ngroup names are: %s" % self.group_list
        self.reset()
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.group_list)):
            return QVariant()
        group_name = self.group_list[index.row()]
        if role == Qt.DisplayRole:
            return QVariant(group_name)
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.group_list)
        
    def columnCount(self, index=QModelIndex()):
        return 1
        
    def setData(self, index, value, role=Qt.EditRole):
        old_name = self.group_list[index.row()]
        new_name = unicode(value.toString().toUtf8(), "utf-8")

        ###
        # we don't allow empty strings for group names; just pass
        # if this happens (typically this will be an accident on the user's part)
        if new_name == "":
            return False
        
        self.dataset.change_group_name(old_name, new_name)#, \
                        #outcome=self.current_outcome, follow_up=self.current_follow_up)
        self.refresh_group_list(self.current_outcome, self.current_follow_up)
        return True
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)

        
class OutcomesModel(QAbstractTableModel):
    '''
    A simple table model for editing/deleting/adding outcomes.
    Subclasses the QAbstractTableModel and provide the fields of interest
    to the view.
    '''
    def __init__(self, filename=QString(), dataset=None):
        super(OutcomesModel, self).__init__()
        self.dataset = dataset
        self.current_outcome = None
        self.outcome_list = self.dataset.get_outcome_names()

        
    def refresh_outcome_list(self):
        self.outcome_list = self.dataset.get_outcome_names()
        self.reset()
        
    def data(self, index, role=Qt.DisplayRole):
        self.outcome_list = self.dataset.get_outcome_names()
        if not index.isValid() or not (0 <= index.row()):
            return QVariant()
        outcome_name = ""
        try:
            outcome_name = self.outcome_list[index.row()]
        except:
            pass
        if role == Qt.DisplayRole:
            return QVariant(outcome_name)
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.outcome_list)
        
    def columnCount(self, index=QModelIndex()):
        return 1
        
    def setData(self, index, value, role=Qt.EditRole):
        old_outcome_name = self.outcome_list[index.row()]
        new_outcome_name = unicode(value.toString().toUtf8(), "utf-8")
        if new_outcome_name == "":
            return False
            
        self.dataset.change_outcome_name(old_outcome_name, new_outcome_name)
        # issue #130: if we change an outcome name, set the current outcome
        # to said outcome
        self.current_outcome = new_outcome_name
        return True
                
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)
                            
class FollowUpsModel(QAbstractTableModel):
    '''
    A simple table model for editing/deleting/adding follow-ups.
    Subclasses the QAbstractTableModel and provide the fields of interest
    to the view.
    '''
    def __init__(self, filename=QString(), dataset=None, outcome = None):
        super(FollowUpsModel, self).__init__()
        self.dataset = dataset
        ## we maintain a current outcome string variable because
        # the follow-ups are outcome specific
        self.current_outcome = outcome
        self.follow_up_list = self.dataset.get_follow_up_names_for_outcome(outcome)
        
    def refresh_follow_up_list(self):  
        self.follow_up_list = self.dataset.get_follow_up_names_for_outcome(self.current_outcome)
        self.reset()
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row()):
            return QVariant()
        follow_up_name = None
        try:
            follow_up_name = self.follow_up_list[index.row()] 
        except:
            pass
            
        if role == Qt.DisplayRole:
            return QVariant(follow_up_name)
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.follow_up_list)
        
    def columnCount(self, index=QModelIndex()):
        return 1
        
    def setData(self, index, value, role=Qt.EditRole):
        old_follow_up_name = self.follow_up_list[index.row()]
        new_follow_up_name = unicode(value.toString().toUtf8(), "utf-8")
        self.dataset.change_follow_up_name(self.current_outcome, old_follow_up_name, new_follow_up_name)
        self.refresh_follow_up_list()
        return True
        
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)
                            
class StudiesModel(QAbstractTableModel):
    '''
    Table model implementation for studies list.
    '''
    def __init__(self, filename=QString(), dataset=None):
        super(StudiesModel, self).__init__()
        self.dataset = dataset
        self.update_study_list()
        
    def update_study_list(self):
        self.studies_list = self.dataset.studies
        self.reset()
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.studies_list)):
            return QVariant()
        study_name = self.studies_list[index.row()].name
        if role == Qt.DisplayRole:
            return QVariant(study_name)
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.studies_list)
        
    def columnCount(self, index=QModelIndex()):
        return 1
        
    def setData(self, index, value, role=Qt.EditRole):
        study_object = self.studies_list[index.row()]
        new_name = unicode(value.toString().toUtf8(), "utf-8")

        ###
        # we don't allow empty strings for group names; just pass
        # if this happens (typically this will be an accident on the user's part)
        if new_name == "":
            return False
        
        study_object.name = new_name
        self.update_study_list()
        return True
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)
                            
class CovariatesModel(QAbstractTableModel):
    '''
    Table model implementation for covariates.
    '''
    def __init__(self, filename=QString(), dataset=None):
        super(CovariatesModel, self).__init__()
        self.dataset = dataset
        self.update_covariates_list()
        
    def update_covariates_list(self):
        self.covariates_list = self.dataset.covariates
        self.reset()
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.covariates_list)):
            return QVariant()
        cov_name = self.covariates_list[index.row()].name
        if role == Qt.DisplayRole:
            return QVariant(cov_name)
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.covariates_list)
        
    def columnCount(self, index=QModelIndex()):
        return 1
        
    def setData(self, index, value, role=Qt.EditRole):
        cov_object = self.covariates_list[index.row()]
        new_name = unicode(value.toString().toUtf8(), "utf-8")

        ###
        # we don't allow empty strings for group names; just pass
        # if this happens (typically this will be an accident on the user's part).
        # nor do we allow covariates to have the same name.
        if new_name == "" or new_name in self.dataset.get_cov_names():
            return False
        
        self.dataset.change_covariate_name(cov_object, new_name)
        self.update_covariates_list()
        return True
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)