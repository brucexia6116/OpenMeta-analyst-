#############################################
#                                           #
#  Byron C. Wallace                         #
#  Tufts Medical Center                     #
#  This is the code for the ui dialog       #
#  that handles the method selection        #
#  and algorithm specifications             #
#                                           #                                                                            
#  OpenMeta[analyst]                        #
#                                           #
#  This is also where the calls to run      #
#  meta-analyses originate, via a callback  #
#  to the go() routine on meta_form.        #
#                                           #
#############################################


from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qt import *
import pdb
import sip

import ui_ma_specs
import meta_py_r
from meta_globals import *

class MA_Specs(QDialog, ui_ma_specs.Ui_Dialog):

    def __init__(self, model, parent=None, meta_f_str=None,
                    external_params=None):
        super(MA_Specs, self).__init__(parent)
        self.setupUi(self)
        self.model = model
        
        # if not none, we assume we're running a meta
        # method 
        self.meta_f_str = meta_f_str

        QObject.connect(self.buttonBox, SIGNAL("accepted()"), self.run_ma)
        QObject.connect(self.buttonBox, SIGNAL("rejected()"), self.cancel)
        QObject.connect(self.save_btn, SIGNAL("pressed()"), self.select_out_path)
        QObject.connect(self.method_cbo_box, SIGNAL("currentIndexChanged(QString)"),
                                             self.method_changed)

        self.data_type = self.model.get_current_outcome_type()
        print "data type: %s" % self.data_type
        if self.meta_f_str is not None:
            # we pre-prend the data type to the meta-method function
            # name. thus the caller (meta_form) needn't worry about
            # the data type, only about the method name (e.g., cumulative)
            self.meta_f_str = ".".join((self.meta_f_str, self.data_type))
            
            
        if self.data_type != "binary":
            self.disable_bin_only_fields()
            
        self.current_widgets = []
        self.current_method = None
        self.current_params = None
        self.current_defaults = None
        self.var_order = None
        self.current_param_vals = external_params or {}
        self.populate_cbo_box()

    def cancel(self):
        print "(cancel)"
        self.reject()

    def select_out_path(self):
        out_f = "."
        out_f = unicode(QFileDialog.getSaveFileName(self, "OpenMeta[analyst] - Plot Path",
                                                    out_f, "png image files: (.png)"))
        if out_f == "" or out_f == None:
            return None
        else:
            self.image_path.setText(out_f)
        
    def run_ma(self):
        result = None
        ### add forest plot parameters
        self.add_plot_params()
        # also add the metric to the parameters
        # -- this is for scaling
        
        if not self.data_type == "diagnostic":
            self.current_param_vals["measure"] = self.model.current_effect 
        
        # dispatch on type; build an R object, then run the analysis
        if self.data_type == "binary":
            # note that this call creates a tmp object in R called
            # tmp_obj (though you can pass in whatever var name
            # you'd like)
            meta_py_r.ma_dataset_to_simple_binary_robj(self.model)
            if self.meta_f_str is None:
                result = meta_py_r.run_binary_ma(self.current_method, self.current_param_vals)
            else:
                result = meta_py_r.run_meta_method(self.meta_f_str, self.current_method, self.current_param_vals)
        elif self.data_type == "continuous":
            meta_py_r.ma_dataset_to_simple_continuous_robj(self.model)
            if self.meta_f_str is None:
                # run standard meta-analysis
                result = meta_py_r.run_continuous_ma(self.current_method, self.current_param_vals)
            else:
                # get meta!
                result = meta_py_r.run_meta_method(self.meta_f_str, self.current_method, self.current_param_vals)
        elif self.data_type == "diagnostic":
            if self.meta_f_str is None:
                #####
                # This is somewhat hacky. We are building up a single
                # dictionary containing results for both sens. and spec.
                # This is constructed by parsing out the results from 
                # individual runs.
                #####
                result = {'images':{}, 'texts':{}, 'image_var_names':{}}
                # This provides us a 'base' path; from this we construc
                # output paths for each individual forest plot (one 
                # per diagnostic metric).
                split_fp_path = self.current_param_vals["fp_outpath"].split(".")
                for diag_metric in ("Sens", "Spec"):
                    self.current_param_vals["measure"] = diag_metric
                    new_str = split_fp_path[0] if len(split_fp_path) == 1 else \
                              ".".join(split_fp_path[:-1])
                    new_str = new_str + "_%s" % diag_metric + ".png"
                    self.current_param_vals["fp_outpath"] = new_str
                    ### build a new MetaAnalysis object with the current metric.
                    meta_py_r.ma_dataset_to_simple_diagnostic_robj(self.model, metric=diag_metric)
                    ### despite looking ok here, this returns the value of the first iteration!!!
                    cur_result = meta_py_r.run_diagnostic_ma(self.current_method, self.current_param_vals)
                    for field in result.keys():
                        for val in cur_result[field].keys():
                            result[field]["%s %s" % (diag_metric, val)] = cur_result[field][val]
                
            else:
                pass
        self.parent().analysis(result)
        self.accept()
    
    def add_plot_params(self):
        ### TODO shouldn't couple R plotting routine with UI so tightly
        self.current_param_vals["fp_show_col1"] = self.show_1.isChecked()
        self.current_param_vals["fp_col1_str"] = unicode(self.col1_str_edit.text().toUtf8(), "utf-8")
        self.current_param_vals["fp_show_col2"] = self.show_2.isChecked()
        self.current_param_vals["fp_col2_str"] = unicode(self.col2_str_edit.text().toUtf8(), "utf-8")
        self.current_param_vals["fp_show_col3"] = self.show_3.isChecked()
        self.current_param_vals["fp_col3_str"] = unicode(self.col3_str_edit.text().toUtf8(), "utf-8")
        self.current_param_vals["fp_show_col4"] = self.show_4.isChecked()
        self.current_param_vals["fp_col4_str"] = unicode(self.col4_str_edit.text().toUtf8(), "utf-8")
        self.current_param_vals["fp_xlabel"] = unicode(self.x_lbl_le.text().toUtf8(), "utf-8")
        self.current_param_vals["fp_outpath"] = unicode(self.image_path.text().toUtf8(), "utf-8")
        plot_lb = unicode(self.plot_lb_le.text().toUtf8(), "utf-8")
        if plot_lb != "[default]" and self.check_plot_bound(plot_lb):
            self.current_param_vals["fp_plot_lb"] = plot_lb
        else:
            self.current_param_vals["fp_plot_lb"] = "NULL"
        plot_ub = unicode(self.plot_ub_le.text().toUtf8(), "utf-8")
        if plot_ub != "[default]" and self.check_plot_bound(plot_ub):
            self.current_param_vals["fp_plot_ub"] = plot_ub
        else:
            self.current_param_vals["fp_plot_ub"] = "NULL"
        xticks = unicode(self.x_ticks_le.text().toUtf8(), "utf-8")
        if xticks != "[default]" and self.seems_sane(xticks):
            self.current_param_vals["fp_xticks"] = xticks
        else:
            self.current_param_vals["fp_xticks"] = "NULL"
        self.current_param_vals["fp_show_summary_line"] = self.show_summary_line.isChecked()
    def seems_sane(self, xticks):
        num_list = xticks.split(",")
        if len(num_list) == 1:
            return False
        try:
            num_list = [eval(x) for x in num_list]
        except:
            return False
        return True
        
    def check_plot_bound(self, bound):
        try:
            eval(bound)
        except:
            return False
        return True
    
    def disable_bin_only_fields(self):
        self.col3_str_edit.setEnabled(False)
        self.col4_str_edit.setEnabled(False)
         

    def method_changed(self):
        self.clear_param_ui()
        self.current_widgets= []
        self.current_method = self.available_method_d[str(self.method_cbo_box.currentText())]
        self.setup_params()
        self.parameter_grp_box.setTitle(self.current_method)
        self.ui_for_params()

    def populate_cbo_box(self):
        # we first build an R object with the current data. this is to pass off         
        # to the R side to check the feasibility of the methods over the current data.
        # i.e., we do not display methods that cannot be performed over the 
        # current data.
        tmp_obj_name = "tmp_obj" 
        if self.data_type == "binary":
            meta_py_r.ma_dataset_to_simple_binary_robj(self.model, var_name=tmp_obj_name)
        elif self.data_type == "continuous":
            meta_py_r.ma_dataset_to_simple_continuous_robj(self.model, var_name=tmp_obj_name)
        elif self.data_type == "diagnostic":
            meta_py_r.ma_dataset_to_simple_diagnostic_robj(self.model, var_name=tmp_obj_name)
            
        self.available_method_d = meta_py_r.get_available_methods(for_data_type=self.data_type, data_obj_name=tmp_obj_name)
        print "\n\navailable %s methods: %s" % (self.data_type, ", ".join(self.available_method_d.keys()))
        for method in self.available_method_d.keys():
            self.method_cbo_box.addItem(method)
        self.current_method = self.available_method_d[str(self.method_cbo_box.currentText())]
        self.setup_params()
        self.parameter_grp_box.setTitle(self.current_method)


    def clear_param_ui(self):
        for widget in self.current_widgets:
            widget.deleteLater()
            widget = None


    def ui_for_params(self):
        if self.parameter_grp_box.layout() is None:
           layout = QGridLayout()
           self.parameter_grp_box.setLayout(layout)

        cur_grid_row = 0
        
        # add the method description
        method_description = meta_py_r.get_method_description(self.current_method)
        
        self.add_label(self.parameter_grp_box.layout(), cur_grid_row, "Description: %s" % method_description)
        cur_grid_row += 1
        
        if self.var_order is not None:
            for var_name in self.var_order:
                val = self.current_params[var_name]
                self.add_param(self.parameter_grp_box.layout(), cur_grid_row, var_name, val)
                cur_grid_row+=1
        else:
            # no ordering was provided; let's try and do something
            # sane with respect to the order in which parameters
            # are displayed.
            #
            # we want to add the parameters in groups, for example,
            # we add combo boxes (which will be lists of values) together,
            # followed by numerical inputs. thus we create an ordered list
            # of functions to check if the argument is the corresponding
            # type (float, list); if it is, we add it otherwise we pass. this isn't
            # the most efficient way to do things, but the number of parameters
            # is going to be relatively tiny anyway
            ordered_types = [lambda x: isinstance(x, list), \
                                        lambda x: isinstance(x, str) and x.lower()=="float"]
    
            for is_right_type in ordered_types:
                for key, val in self.current_params.items():
                    if is_right_type(val):
                        self.add_param(self.parameter_grp_box.layout(), cur_grid_row, key, val)
                        cur_grid_row+=1

    def add_param(self, layout, cur_grid_row, name, value):
        print "adding param. name: %s, value: %s" % (name, value)
        if isinstance(value, list):
            # then it's an enumeration of values
            self.add_enum(layout, cur_grid_row, name, value)
        elif value.lower() == "float":
            self.add_float_box(layout, cur_grid_row, name)
        else:
            print "unknown type! throwing up. bleccch."
            print "name:%s. value: %s" % (name, value)
            # throw exception here

    def add_enum(self, layout, cur_grid_row, name, values):
        '''
        Adds an enumeration to the UI, with the name and possible
        values as specified per the parameters.
        '''
        
        ### 
        # using the pretty name for the label now.
        self.add_label(layout, cur_grid_row, self.param_d[name]["pretty.name"], \
                                tool_tip_text=self.param_d[name]["description"])
        cbo_box = QComboBox()
        for value in values:
            cbo_box.addItem(value)

        if self.current_defaults.has_key(name):
            cbo_box.setCurrentIndex(cbo_box.findText(self.current_defaults[name]))
            self.current_param_vals[name] = self.current_defaults[name]

        QObject.connect(cbo_box, QtCore.SIGNAL("currentIndexChanged(QString)"),
                                 self.set_param_f(name))

        self.current_widgets.append(cbo_box)
        layout.addWidget(cbo_box, cur_grid_row, 1)

    def add_float_box(self, layout, cur_grid_row, name):
        self.add_label(layout, cur_grid_row, self.param_d[name]["pretty.name"],\
                                tool_tip_text=self.param_d[name]["description"])
        # now add the float input line edit
        finput = QLineEdit()

        # if a default value has been specified, use it
        if self.current_defaults.has_key(name):
            finput.setText(str(self.current_defaults[name]))
            self.current_param_vals[name] = self.current_defaults[name]

        finput.setMaximumWidth(50)
        QObject.connect(finput, QtCore.SIGNAL("textChanged(QString)"),
                                 self.set_param_f(name, to_type=float))
        self.current_widgets.append(finput)
        layout.addWidget(finput, cur_grid_row, 1)

    def set_param_f(self, name, to_type=str):
        '''
        Returns a function f(x) such that f(x) will set the key
        name in the parameters dictionary to the value x.
        '''
        def set_param(x):
            self.current_param_vals[name] = to_type(x)
            print self.current_param_vals

        return set_param

    def add_label(self, layout, cur_grid_row, name, tool_tip_text = None):
        lbl = QLabel(name, self.parameter_grp_box)
        if not tool_tip_text is None:
            lbl.setToolTip(tool_tip_text)
        self.current_widgets.append(lbl)
        layout.addWidget(lbl, cur_grid_row, 0)

    def setup_params(self):
        # parses out information about the parameters of the current method
        # param_d holds (meta) information about the parameter -- it's a each param
        # itself maps to a dictionary with a pretty name and description (assuming
        # they were provided for the given param)
        self.current_params, self.current_defaults, self.var_order, self.param_d = \
                    meta_py_r.get_params(self.current_method)
        print self.current_defaults
