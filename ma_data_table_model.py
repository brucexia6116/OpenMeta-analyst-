#########################################################################################
#                                                                                       #
#  Byron C. Wallace                                                                     #
#  Tufts Medical Center                                                                 #
#  OpenMeta[analyst]                                                                    #
#  ---                                                                                  #
#  Proxy class, interfaces between the underlying representation (in ma_dataset.py)     #
#  and the DataTableView UI. Basically deals with keeping track of which outcomes/      #
#  follow-ups/treatments are being viewed. See Summerfield's chapters on M-V-C          #
# in "Rapid GUI Programming with Python and QT" for an overview of the architecture.    #
#########################################################################################

# core libraries
import PyQt4
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtRemoveInputHook
import pdb

# home-grown
import ma_dataset
from ma_dataset import *
import meta_py_r
import meta_globals 
from meta_globals import *

class DatasetModel(QAbstractTableModel):
    '''
    This module mediates between the classes comprising a dataset
    (i.e., study & ma_unit objects) and the view. In particular, we
    subclass the QAbstractTableModel and provide the fields of interest
    to the view.

    Apologies for the mixing of camelCase and lower_case style method
    names; the former are due to the QT framework, but I just couldn't
    bring myself to maintain this blighted style.
    '''
    def __init__(self, filename=QString(), dataset=None):
        super(DatasetModel, self).__init__()

        self.dataset = dataset or Dataset()
        # include an extra blank study to begin with
        self.dataset.studies.append(Study(self.max_study_id() +1))

        # these variables track which meta-analytic unit,
        # i.e., outcome and time period, are being viewed
        self.current_outcome = None
        self.current_time_point = 0
        
        # we also track which groups are being viewed
        self.tx_index_a = 0
        self.tx_index_b = 1

        self.update_current_group_names()
            
        #
        # column indices; these are a core component of this class,
        # as these indices are what maps the UI to the model. The following
        # columns are constant across datatypes, but some (e.g., the 
        # columns corresponding to raw data) are variable. see the
        # update_column_indices method for more.
        self.INCLUDE_STUDY = 0
        self.NAME, self.YEAR = [col+1 for col in range(2)]
        self.update_column_indices()
           
        # @TODO parameterize; make variable
        self.current_effect = "OR"

        # @TODO presumably the COVARIATES will contain the column
        # indices and the currently_displayed... will contain the names
        # of the covariates being displayed in said columns, in order
        self.COVARIATES = None
        self.currently_displayed_covariates = []

        # @TODO
        self.LABELS = None
        self.headers = ["include", "study name", "year"]

        self.NUM_DIGITS = 3
        self.study_auto_added = None


    def set_current_metric(self, metric):
        self.current_effect = metric
        print "OK! metric updated."
        
    def update_current_outcome(self):
        outcome_names = self.dataset.get_outcome_names()

        ###
        # @TODO we need to maintain a current outcome
        # index here, as we do for groups (below), so that
        # when the user edits the currently displayed outcome,
        # the edited outcome is shown in its place
        self.current_outcome = outcome_names[0] if len(outcome_names)>0 else None
        print self.current_outcome
        self.reset()
        
    def update_current_time_points(self):
        if self.current_outcome is not None:
            # note that the user cannot delete all follow-ups; so it's safe to assume this dictionary has 
            # at least one entry
            self.current_time_point = self.dataset.outcome_names_to_follow_ups[self.current_outcome].keys()[0]
        else:
            self.current_time_point = 0
        self.reset()
        
    def update_current_group_names(self):
        '''
        This is to be called after the model has been
        edited (via, e.g., the edit_dialog module)
        '''
        group_names = self.dataset.get_group_names()        
        n_groups = len(group_names)

        if n_groups > 1:
            # make sure the indices are within range -- the
            # model may have changed without our knowing.
            # may have been nicer to have a notification
            # framework here (i.e., have the udnerlying model
            # notify us when a group has been deleted) rather
            # than doing it on the fly...
            self.tx_index_a = self.tx_index_a % n_groups
            self.tx_index_b = self.tx_index_b % n_groups
            while self.tx_index_a == self.tx_index_b:
                self._next_group_indices(group_names)
            self.current_txs = [group_names[self.tx_index_a], group_names[self.tx_index_b]]
        else:
            self.current_txs = ["tx A", "tx B"]
        self.previous_txs = self.current_txs
        self.reset()
        
    def update_column_indices(self):
        # Here we update variable column indices, contingent on 
        # the type data being displayed, the number of covariates, etc. 
        # It is extremely important that these are updated as necessary
        # from the view side of things
        current_data_type = self.get_current_outcome_type()
        # offset corresonds to the first three columns, which 
        # are include study, name, and year.
        offset = 3
        if current_data_type == "binary":
            self.RAW_DATA = [col+offset for col in range(4)]
            self.OUTCOMES = [7, 8, 9]
        elif current_data_type == "continuous":
            self.RAW_DATA = [col+offset for col in range(6)]
            self.OUTCOMES = [9, 10, 11] 
        else:
            # diagnostic
            # @TODO what to do about 'other'?
            self.RAW_DATA = [col+offset for col in range(4)]
            # sensitivity & specificity? 
            self.OUTCOMES = [7, 8]
            
    def data(self, index, role=Qt.DisplayRole):
        '''
        Implements the required QTTableModel data method. There is a lot of switching on 
        role/index/datatype here, but this seems consistent with the QT paradigm (see 
        Summerfield's book)
        '''
        if not index.isValid() or not (0 <= index.row() < len(self.dataset)):
            return QVariant()
        study = self.dataset.studies[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == self.NAME:
                return QVariant(study.name)
            elif column == self.YEAR:
                if study.year == 0:
                    return QVariant("")
                else:
                    return QVariant(study.year)
            elif self.current_outcome is not None and column in self.RAW_DATA:
                adjusted_index = column - 3
                if self.current_outcome in study.outcomes_to_follow_ups:
                    cur_raw_data = self.get_current_ma_unit_for_study(index.row()).\
                                                        get_raw_data_for_groups(self.current_txs)                                 
                    if len(cur_raw_data) > adjusted_index:
                        return QVariant(cur_raw_data[adjusted_index])
                    else:
                        return QVariant("")
                else:
                    return QVariant("")
            elif column in self.OUTCOMES:
                # either the point estimate, or the lower/upper
                # confidence interval
                outcome_index = column - self.OUTCOMES[0]
                est_and_ci = self.get_current_ma_unit_for_study(index.row()).\
                                                get_display_effect_and_ci(self.current_effect)
                outcome_val = est_and_ci[outcome_index]
                if outcome_val is None:
                    return QVariant("")
                outcome_val = est_and_ci[outcome_index]
                return QVariant(round(outcome_val, self.NUM_DIGITS))
            elif column != self.INCLUDE_STUDY:
                # here the column is to the right of the outcomes (and not the 0th, or
                # 'include study' column, and thus must corrrespond to a covariate.
                cov_name = self.get_cov(column).name
                cov_value = study.covariate_dict[cov_name] if \
                    study.covariate_dict.has_key(cov_name) else None
                if cov_value is None:
                    cov_value = ""
                return QVariant(cov_value)
                
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        elif role == Qt.CheckStateRole:
            # this is where we deal with the inclusion/exclusion of studies
            if column == self.INCLUDE_STUDY:
               checked_state = Qt.Unchecked
               if index.row() < self.rowCount()-1 and study.include:
                   checked_state = Qt.Checked
               return QVariant(checked_state)
        elif role == Qt.BackgroundColorRole:
            if column in self.OUTCOMES:
                return QVariant(QColor(Qt.yellow))
            elif column in self.RAW_DATA[len(self.RAW_DATA)/2:] and \
                        self.current_effect in ONE_ARM_METRICS:
                return QVariant(QColor(Qt.gray))
            else:
                return QVariant(QColor(Qt.white))
        return QVariant()


    def setData(self, index, value, role=Qt.EditRole):
        '''
        Implementation of the AbstractDataTable method. The view uses this method
        to request data to display. Thus we here return values to render in the table
        based on the index (row, column).

        For more, see: http://doc.trolltech.com/4.5/qabstracttablemodel.html
        '''
        if index.isValid() and 0 <= index.row() < len(self.dataset):
            current_data_type = self.dataset.get_outcome_type(self.current_outcome)
            column = index.column()
            old_val = self.data(index)
            study = self.dataset.studies[index.row()]
            if column in (self.NAME, self.YEAR):
                if column == self.NAME:
                    study.name = unicode(value.toString().toUtf8(), encoding="utf8")
                    if study.name != "" and index.row() == self.rowCount()-1:
                        # if the last study was just edited, append a
                        # new, blank study
                        # TODO bug: if a new tx group is added, and then a new study
                        # is added, the program throws up because the study doesn't have
                        # the new outcome in its meta-analytic unit object -- need to check
                        # for this at runtime as we do with follow-up and outcome
                        new_study = Study(self.max_study_id()+1)
                        self.dataset.add_study(new_study)
                        self.study_auto_added = int(new_study.id)
                        self.reset()
                else:
                    study.year = value.toInt()[0]
            elif self.current_outcome is not None and column in self.RAW_DATA:
                # @TODO make module-level constant?
                adjust_by = 3 # include study, study name, year columns
                ma_unit = self.get_current_ma_unit_for_study(index.row())
                group_name = self.current_txs[0]
                if current_data_type == BINARY:
                    if column in self.RAW_DATA[2:]:
                        adjust_by += 2 
                        group_name = self.current_txs[1]
                elif current_data_type == CONTINUOUS:
                    if column in self.RAW_DATA[3:]:
                        adjust_by += 3
                        group_name = self.current_txs[1]
                        
                adjusted_index = column-adjust_by
                val = value.toDouble()[0] if value.toDouble()[1] else ""
                ma_unit.tx_groups[group_name].raw_data[adjusted_index] = val
                # If a raw data column value is being edit, attempt to
                # update the corresponding outcome (if data permits)
                self.update_outcome_if_possible(index.row())
            elif column in self.OUTCOMES:
                # the user can also explicitly set the effect size / CIs
                # @TODO what to do if the entered estimate contradicts the raw data?
                display_scale_val, converted_ok = value.toDouble()
                if converted_ok:
                    # note that we convert from the display/continuous
                    # scale on which the metric is assumed to have been
                    # entered into the 'calculation' scale (e.g., log)
                    calc_scale_val = None
                    if current_data_type == BINARY:
                        calc_scale_val = meta_py_r.binary_convert_scale(display_scale_val, \
                                                    self.current_effect, convert_to="calc.scale")
                    else:
                        ## assuming continuous here
                        calc_scale_val = meta_py_r.continuous_convert_scale(display_scale_val, \
                                                    self.current_effect, convert_to="calc.scale")
                                                    
                    ma_unit = self.get_current_ma_unit_for_study(index.row())
                    if column == self.OUTCOMES[0]:
                        ma_unit.set_effect(self.current_effect, calc_scale_val)
                        ma_unit.set_display_effect(self.current_effect, display_scale_val)
                    elif column == self.OUTCOMES[1]:
                        # lower
                        ma_unit.set_lower(self.current_effect, calc_scale_val)
                        ma_unit.set_display_lower(self.current_effect, display_scale_val)
                    else:
                        # upper
                        ma_unit.set_upper(self.current_effect, calc_scale_val)
                        ma_unit.set_display_upper(self.current_effect, display_scale_val)
            elif column == self.INCLUDE_STUDY:
                study.include = value.toBool()
                # we keep note if a study was manually 
                # excluded; this differs from just being
                # `included' because the latter is TRUE
                # automatically when a study first acquires
                # sufficient data to be included in an MA
                if not value.toBool():
                    study.manually_excluded = True
            else:
                # then a covariate value has been edited.
                cov = self.get_cov(column)
                cov_name = cov.name
                new_value = None
                if cov.data_type == FACTOR:
                    new_value = value.toString()
                else:
                    # continuous
                    new_value, converted_ok = value.toDouble()
                    if not converted_ok: 
                        new_value = None
                study.covariate_dict[cov_name] = new_value
                
            self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)

            # Tell the view that an entry in the table has changed, and what the old
            # and new values were. This for undo/redo purposes.
            new_val = self.data(index)
            self.emit(SIGNAL("cellContentChanged(QModelIndex, QVariant, QVariant)"), index, old_val, new_val)
         
            if self.current_outcome is not None:
                effect_d = self.get_current_ma_unit_for_study(index.row()).effects_dict[self.current_effect]
                # if any of the effect values are empty, we cannot include this study in the analysis, so it
                # is automatically excluded.
                if any([val is None for val in [effect_d[effect_key] for effect_key in ("upper", "lower", "est")]]):
                    study.include = False
                # if the study has not been explicitly excluded by the user, then we automatically
                # include it once it has sufficient data.
                elif not study.manually_excluded:
                    study.include = True
                
            return True
        return False


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        '''
        Implementation of the abstract method inherited from the base table
        model class. This is responsible for providing header data for the
        respective columns.
        '''
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            outcome_type = self.dataset.get_outcome_type(self.current_outcome)
            if section == self.INCLUDE_STUDY:
                return QVariant(self.headers[self.INCLUDE_STUDY])
            elif section == self.NAME:
                return QVariant(self.headers[self.NAME])
            elif section == self.YEAR:
                return QVariant(self.headers[self.YEAR])
            # note that we're assuming here that raw data
            # always shows only two tx groups at once.
            elif self.current_outcome is not None and section in self.RAW_DATA:
                # switch on the outcome type 
                current_tx = self.current_txs[0] # i.e., the first group
                if outcome_type== BINARY:
                    if section in self.RAW_DATA[2:]:
                        current_tx = self.current_txs[1]
                        
                    if section in (self.RAW_DATA[0], self.RAW_DATA[2]):
                        return QVariant(current_tx + " n")
                    else:
                        return QVariant(current_tx + " N")
                elif outcome_type == CONTINUOUS:
                    # continuous data
                    if section in self.RAW_DATA[3:]:
                        current_tx = self.current_txs[1]
                    if section in (self.RAW_DATA[0], self.RAW_DATA[3]):
                        return QVariant(current_tx + " N")
                    elif section in (self.RAW_DATA[1], self.RAW_DATA[4]):
                        return QVariant(current_tx + " mean")
                    else:
                        return QVariant(current_tx + " SD")
            elif section in self.OUTCOMES:
                if outcome_type == BINARY:
                    # effect size, lower CI, upper CI
                    if section == self.OUTCOMES[0]:
                        return QVariant(self.current_effect)
                    elif section == self.OUTCOMES[1]:
                        return QVariant("lower")
                    else:
                        return QVariant("upper")
                elif outcome_type == CONTINUOUS:
                    if section == self.OUTCOMES[0]:
                        return QVariant(self.current_effect)
                    elif section == self.OUTCOMES[1]:
                        return QVariant("lower")
                    else:
                        return QVariant("upper")
            else:
                # then the column is to the right of the outcomes, and must
                # be a covariate.
                cov_name = self.get_cov(section).name
                return QVariant(cov_name)
        
        # this is the vertical -- non-table header -- case.
        # we just show row numbers (not zero-based; hence the +1).
        return QVariant(int(section+1))


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        elif index.column() == self.INCLUDE_STUDY:
             return Qt.ItemFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled |
                            Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)

    def rowCount(self, index=QModelIndex()):
        return self.dataset.num_studies()

    def columnCount(self, index=QModelIndex()):
        return self._get_col_count()

    def get_cov(self, table_col_index):
        # we map (ie, adjust) the table column index to the covariate
        # index. if there is currently an outcome, this means we are
        # subtract off the indices up to the last outcomes column; otherwise
        # we just subtract the include, study name and year columns (giving 3)
        cov_index = table_col_index - (self.OUTCOMES[-1]+1) if \
                        self.current_outcome is not None else table_col_index - 3
        return self.dataset.covariates[cov_index]
        
    def _get_col_count(self):
        '''
        Calculate how many columns to display; this is contingent on the data type,
        amongst other things (e.g., number of covariates).
        '''
        num_cols = 3 # we always show study name and year (and include studies)
        if len(self.dataset.get_outcome_names()) > 0:
            num_effect_size_fields = 3 # point estimate, low, high
            num_cols += num_effect_size_fields + self.num_data_cols_for_current_unit()
        # now add the covariates (if any)
        num_cols += len(self.dataset.covariates)
        return num_cols
        
    def get_ordered_study_ids(self):
        return [study.id for study in self.dataset.studies]

    def add_new_outcome(self, name, data_type):
        data_type = STR_TO_TYPE_DICT[data_type.lower()]
        self.dataset.add_outcome(Outcome(name, data_type))

    def remove_outcome(self, outcome_name):
        self.dataset.remove_outcome(outcome_name)
        
    def add_new_group(self, name):
        self.dataset.add_group(name, self.current_outcome)
        
    def remove_group(self, group_name):
        self.dataset.remove_group(group_name)
    
    def add_follow_up_to_current_outcome(self, follow_up_name):
        self.dataset.add_follow_up_to_outcome(self.current_outcome, follow_up_name)
        
    def remove_follow_up_from_outcome(self, follow_up_name, outcome_name):
        self.dataset.remove_follow_up_from_outcome(follow_up_name, outcome_name)
        
    def add_covariate(self, covariate_name, covariate_type, cov_values=None):
        self.dataset.add_covariate(Covariate(covariate_name, covariate_type), cov_values=cov_values)
        self.reset()
    
    def remove_covariate(self, covariate_name):
        self.dataset.remove_covariate(covariate_name)
        self.reset()
        
    def remove_study(self, id):
        self.dataset.studies.pop(id)
        self.reset()

    def get_next_outcome_name(self):
        outcomes = self.dataset.get_outcome_names()
        cur_index = outcomes.index(self.current_outcome)
        next_outcome = outcomes[0] if cur_index == len(outcomes)-1\
                                                        else outcomes[cur_index+1]
        return next_outcome

    def get_prev_outcome_name(self):
        outcomes = self.dataset.get_outcome_names()
        cur_index = outcomes.index(self.current_outcome)
        prev_outcome = outcomes[-1] if cur_index == 0 \
                                                        else outcomes[cur_index-1]
        return prev_outcome

    def get_next_follow_up(self):
        print "\nfollow ups for outcome:"
        print self.dataset.outcome_names_to_follow_ups[self.current_outcome]
        t_point = self.current_time_point
        if self.current_time_point >= max(self.dataset.outcome_names_to_follow_ups[self.current_outcome].keys()):
            t_point = 0
        else:
            # WARNING if we delete a time point things might get screwed up here
            # as we're actually using the MAX when we insert new follow ups
            # TODO change this to look for the next greatest time point rather than
            # assuming the current + 1 exists
            t_point += 1
        follow_up_name = self.get_follow_up_name_for_t_point(t_point)
        print "\nt_point; name: %s, %s" % (t_point, follow_up_name)
        return (t_point, follow_up_name)
        
    def get_previous_follow_up(self):
        t_point = self.current_time_point
        if self.current_time_point <= min(self.dataset.outcome_names_to_follow_ups[self.current_outcome].keys()):
            t_point = max(self.dataset.outcome_names_to_follow_ups[self.current_outcome].keys())
        else:
            # WARNING if we delete a time point things might get screwed up here
            # as we're actually using the MAX when we insert new follow ups
            # TODO change this to look for the next greatest time point rather than
            # assuming the current - 1 exists
            t_point -= 1
        return (t_point, self.get_follow_up_name_for_t_point(t_point))
        
    def set_current_time_point(self, time_point):
        self.current_time_point = time_point
        self.emit(SIGNAL("followUpChanged()"))
        self.reset()
        
    def set_current_follow_up(self, follow_up_name):
        t_point = self.dataset.outcome_names_to_follow_ups[self.current_outcome].get_key(follow_up_name)
        self.set_current_time_point(t_point)

    def get_current_follow_up_name(self):
        if len(self.dataset.outcome_names_to_follow_ups) > 0:
            try:
                return self.dataset.outcome_names_to_follow_ups[self.current_outcome][self.current_time_point]
            except:
                return None
            
    def get_follow_up_name_for_t_point(self, t_point):
        return self.dataset.outcome_names_to_follow_ups[self.current_outcome][t_point]
        
    def get_t_point_for_follow_up_name(self, follow_up):
        return self.dataset.outcome_names_to_follow_ups[self.current_outcome].get_key(follow_up)
        
    def get_current_groups(self):
        return self.current_txs
        
    def get_previous_groups(self):
        return self.previous_txs
        
    def next_groups(self):
        ''' Returns a tuple with the next two group names (we just iterate round-robin) '''
        ## notice that we only retrieve the group names that belong
        # to the current outcome/follow-up tuple
        group_names = self.dataset.get_group_names_for_outcome_fu(self.current_outcome, self.get_current_follow_up_name())

        self._next_group_indices(group_names)
        while self.tx_index_a == self.tx_index_b:
            self._next_group_indices(group_names)
            
        next_txs = [group_names[self.tx_index_a], group_names[self.tx_index_b]]
        print "new tx group indices a, b: %s, %s" % (self.tx_index_a, self.tx_index_b)
        return next_txs
        
    def _next_group_indices(self, group_names):
        print "\ngroup names: %s" % group_names
        if self.tx_index_b < len(group_names)-1:
            self.tx_index_b += 1
        else:
            # bump the a index
            if self.tx_index_a < len(group_names)-1:
                self.tx_index_a += 1
            else:
                self.tx_index_a = 0
            self.tx_index_b = 0
        
    def outcome_has_follow_up(self, outcome, follow_up):
        ## we just pull the outcome from the first study; we tacitly
        # assume that all studies have the same outcomes/follow-ups
        outcome_d = self.dataset.studies[0].outcomes_to_follow_ups[outcome]   
        return follow_up in outcome_d.keys()
        
    def outcome_fu_has_group(self, outcome, follow_up, group):
        ## we just pull the outcome from the first study; we tacitly
        # assume that all studies have the same outcomes/follow-ups
        outcome_d = self.dataset.studies[0].outcomes_to_follow_ups[outcome]
        ## we _assume_ that the follow_up is in this outcome!
        return group in outcome_d[follow_up].tx_groups.keys()
    
    def set_current_groups(self, group_names):
        self.previous_txs = self.current_txs
        self.current_txs = group_names
        self.tx_index_a = self.dataset.get_group_names().index(group_names[0])
        self.tx_index_b = self.dataset.get_group_names().index(group_names[1])
        print "\ncurrent tx group index a, b: %s, %s" % (self.tx_index_a, self.tx_index_b)

    def sort_studies(self, col, reverse):
        if col == self.NAME:
            self.dataset.studies.sort(cmp = self.dataset.cmp_studies(compare_by="name", reverse=reverse), reverse=reverse)
        elif col == self.YEAR:
            self.dataset.studies.sort(cmp = self.dataset.cmp_studies(compare_by="year", reverse=reverse), reverse=reverse)
        elif col > self.OUTCOMES[-1]:
            cov = self.get_cov(col)
            self.dataset.studies.sort(cmp = self.dataset.cmp_studies(compare_by=cov.name, reverse=reverse), reverse=reverse)
            
        self.reset()

    def order_studies(self, ids):
        ''' Shuffles studies vector to the order specified by ids'''
        ordered_studies = []
        for id in ids:
            for study in self.dataset.studies:
                if study.id == id:
                    ordered_studies.append(study)
                    break
        self.dataset.studies = ordered_studies
        self.reset()

    def set_current_outcome(self, outcome_name):
        self.current_outcome = outcome_name
        self.update_column_indices()
        self.update_cur_tx_effect()
        self.emit(SIGNAL("outcomeChanged()"))
        self.reset()
        
    def update_cur_tx_effect(self):
        outcome_type = self.dataset.get_outcome_type(self.current_outcome)
        if outcome_type == BINARY:
            self.current_effect = "OR"
        elif outcome_type == CONTINUOUS:
            self.current_effect = "MD"
        
    def max_study_id(self):
        if len(self.dataset.studies) == 0:
            return -1
        return max([study.id for study in self.dataset.studies])

    def num_data_cols_for_current_unit(self):
        '''
        Returns the number of columns needed to display the raw data
        given the current data type (binary, etc.)
        
        Note again that outcome names are necessarily unique!
        '''
        data_type = self.dataset.get_outcome_type(self.current_outcome)
        if data_type is None:
            return 0
        elif data_type in [BINARY, DIAGNOSTIC, OTHER]:
            return 4
        else:
            # continuous
            return 6

    def get_current_outcome_type(self, get_str=True):
        ''' Returns the type of the currently displayed (or 'active') outcome (e.g., binary).  '''
        return self.dataset.get_outcome_type(self.current_outcome, get_string=get_str)

    def get_stateful_dict(self):
        '''
        This captures the state of the model view; things like the current outcome
        and column indices that are on the QT side of the data table model.
        '''
        d = {}

        # column indices
        d["NAME"] = self.NAME
        d["YEAR"] = self.YEAR
        d["RAW_DATA"] = self.RAW_DATA
        d["OUTCOMES"] = self.OUTCOMES
        d["HEADERS"] = self.headers

        # currently displayed outcome, etc
        d["current_outcome"] = self.current_outcome
        d["current_time_point"] = self.current_time_point
        d["current_txs"] = self.current_txs
        d["current_effect"] = self.current_effect
        d["study_auto_added"] = self.study_auto_added
        
        return d

    def set_state(self, state_dict):
        for key, val in state_dict.items():
            exec("self.%s = val" % key)

        self.reset()

    def raw_data_is_complete_for_study(self, study_index):
        if self.current_outcome is None or self.current_time_point is None:
            return False

        raw_data = self.get_cur_raw_data_for_study(study_index)
        return not "" in raw_data

    def try_to_update_outcomes(self):
        for study_index in range(len(self.dataset.studies)):
            self.update_outcome_if_possible(study_index)

    def update_outcome_if_possible(self, study_index):
        '''
        Checks the parametric study to ascertain if enough raw data has been
        entered to compute the outcome. If so, the outcome is computed and
        displayed.
        '''
        est_and_ci_d = None
        
        data_type = self.get_current_outcome_type(get_str=False)  
        if self.raw_data_is_complete_for_study(study_index):
            if data_type == BINARY:
                e1, n1, e2, n2 = self.get_cur_raw_data_for_study(study_index)
                print self.current_effect
                if self.current_effect in BINARY_TWO_ARM_METRICS:
                    est_and_ci_d = meta_py_r.effect_for_study(e1, n1, e2, n2, metric=self.current_effect)
                else:
                    # binary, one-arm
                    est_and_ci_d = meta_py_r.effect_for_study(e1, n1, \
                                        two_arm=False, metric=self.current_effect)
            elif data_type == CONTINUOUS:
                n1, m1, se1, n2, m2, se2 = self.get_cur_raw_data_for_study(study_index)
                est_and_ci_d = meta_py_r.continuous_effect_for_study(n1, m1, se1, n2, m2, se2)
   
            est, lower, upper = None, None, None
            if est_and_ci_d is not None:
                est, lower, upper = est_and_ci_d["calc_scale"] # calculation scale
                disp_est, disp_lower, disp_upper = est_and_ci_d["display_scale"] # transformed/dispaly scale
            ma_unit = self.get_current_ma_unit_for_study(study_index)
            # now set the effect size & CIs
            # note that we keep two versions around; a version on the 'calculation' scale
            # (e.g., log) and a version on the continuous/display scale to present to the
            # user via the UI.
            ma_unit.set_effect_and_ci(self.current_effect, est, lower, upper)
            ma_unit.set_display_effect_and_ci(self.current_effect, disp_est, disp_lower, disp_upper)
        
    def get_cur_raw_data(self, only_if_included=True):
        raw_data = []
        for study_index in range(len(self.dataset.studies)):
            if not only_if_included or self.dataset.studies[study_index].include:
                raw_data.append(self.get_cur_raw_data_for_study(study_index))
        # we lop off the last entry because it is always a blank line/study
        ## TODO we should really just check the .include field on the study, as
        # above here. at current, new studies (i.e., auto-added) have their 'include'
        # field set to true for some reason
        return raw_data[:-1]
                
    def included_studies_have_raw_data(self):
        ''' 
        True iff all _included_ studies have all raw data (e.g., 2x2 for binary) for the currently
        selected outcome and tx groups.
        '''
        # the -1 is again accounting for the last (empty) appended study
        for study_index in range(len(self.dataset.studies)-1):
            if self.dataset.studies[study_index].include:
                if not self.raw_data_is_complete_for_study(study_index):
                    return False
        return True


    def study_has_point_est(self, study_index):
        cur_ma_unit = self.get_current_ma_unit_for_study(study_index)
        for x in ("est", "lower", "upper"):
            if cur_ma_unit.effects_dict[self.current_effect][x] is None:
                print "study %s does not have a point estimate" % study_index
                return False
        return "ok -- has all point estimates"
        return True
        
    def cur_point_est_and_SE_for_study(self, study_index):
        cur_ma_unit = self.get_current_ma_unit_for_study(study_index)
        est = cur_ma_unit.effects_dict[self.current_effect]["est"] 
        lower, upper = cur_ma_unit.effects_dict[self.current_effect]["lower"], \
                                cur_ma_unit.effects_dict[self.current_effect]["upper"]
        
        ## TODO make application global!
        mult = 1.96 
        se = (upper-est) /mult
        return (est, se)
        
    def get_cur_ests_and_SEs(self, only_if_included=True):
        ests, SEs = [], []
        for study_index in range(len(self.dataset.studies)-1):
            if not only_if_included or self.dataset.studies[study_index].include:
                est, SE = self.cur_point_est_and_SE_for_study(study_index)
                ests.append(est)
                SEs.append(SE)
        return (ests, SEs)
        
    def included_studies_have_point_estimates(self):
        ''' 
        True iff all included studies have all point estiamtes (and CIs) for the
        selected outcome and tx groups.
        '''
        for study_index in range(len(self.dataset.studies)-1):
            if self.dataset.studies[study_index].include:
                if not self.study_has_point_est(study_index):
                    return False
        return True    
        
    def get_studies(self, only_if_included=True):
        included_studies = []
        for study in self.dataset.studies:
            if not only_if_included or study.include:
                included_studies.append(study)
        # we lop off the last entry because it is always a blank line/study
        return list(included_studies[:-1])      
        
    def get_cur_raw_data_for_study(self, study_index):
        return self.get_current_ma_unit_for_study(study_index).get_raw_data_for_groups(self.current_txs)

    def set_current_ma_unit_for_study(self, study_index, new_ma_unit):
        # note that we just assume this exists.
        self.dataset.studies[study_index].outcomes_to_follow_ups[self.current_outcome][self.get_current_follow_up_name()]=new_ma_unit
        
    def get_current_ma_unit_for_study(self, study_index):
        '''
        Returns the MetaAnalytic unit for the study @ study_index. If no such Unit exists,
        it will be added. Thus when a new study is added to a dataset, there is no need
        to initially populate this study with empty MetaAnalytic units reflecting the known
        outcomes, time points & tx groups, as they will be added 'on-demand' here.
        '''
        # first check to see that the current outcome is contained in this study
        if not self.current_outcome in self.dataset.studies[study_index].outcomes_to_follow_ups:
            ###
            # Issue 7 (RESOLVED) http://github.com/bwallace/OpenMeta-analyst-/issues/#issue/7
            # previously, 
            self.dataset.studies[study_index].add_outcome(self.dataset.get_outcome_obj(self.current_outcome), \
                                                                                                group_names=self.dataset.get_group_names())
        
        # we must also make sure the time point exists. note that we use the *name* rather than the 
        # index of the current time/follow up
        if not self.get_current_follow_up_name() in self.dataset.studies[study_index].outcomes_to_follow_ups[self.current_outcome]:
            self.dataset.studies[study_index].add_outcome_at_follow_up(
                                self.dataset.get_outcome_obj(self.current_outcome), self.get_current_follow_up_name())
        
        # finally, make sure the studies contain the currently selected tx groups; if not, add them
        ma_unit = self.dataset.studies[study_index].outcomes_to_follow_ups[self.current_outcome][self.get_current_follow_up_name()]
        for tx_group in self.current_txs:
            if not tx_group in ma_unit.get_group_names():
                ma_unit.add_group(tx_group)
        
        return ma_unit


    def get_ma_unit(self, study_index, outcome, follow_up):
        try:
            return self.dataset.studies[study_index].outcomes_to_follow_ups[outcome][follow_up]
        except:
            raise Exception, "whoops -- you're attempting to access raw data for a study, outcome \
                                        or time point that doesn't exist."
        
    def max_raw_data_cols_for_current_unit(self):
        '''
        Returns the length of the biggest raw data list for the parametric ma_unit. e.g.,
        if a two group, binary outcome is the current ma_unit, then the studies should
        raw data vectors that contain, at most, 4 elements.
        '''
        return \
          max([len(\
            study.outcomes_to_follow_ups[self.current_outcome][self.current_time_point].get_raw_data_for_groups(self.current_txs)\
          ) for study in self.dataset.studies if self.current_outcome in study.outcomes_to_follow_ups])



