from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QColorDialog, QMessageBox
import sys
from collections import defaultdict
from random import randint
from pandas import DataFrame

from REI_calc_main_design import Ui_MainWindow
from settings_window import Ui_SettingsDialog
import REI_Calculations
import data_output 


class SettingsWindow(QDialog):
    caption_bgcolor = "#ffbf00"
    special_row_bgcolor = "#359aa5"

    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.set_default_colors()

    def set_default_colors(self):
        settings = QtCore.QSettings("calculator_settings")
        if not settings.value("caption_bgcolor"):
            settings.setValue("caption_bgcolor", self.caption_bgcolor)
            settings.setValue("special_row_bgcolor", self.caption_bgcolor)

        # set default colors
        color_name = "QPushButton { background-color: color_name }".replace(
            "color_name", self.caption_bgcolor
        )
        self.ui.caption_bgcolor_button.setStyleSheet(color_name)
        self.ui.caption_bgcolor_button.setText("")
        color_name = "QPushButton { background-color: color_name }".replace(
            "color_name", self.special_row_bgcolor
        )
        self.ui.special_row_bgcolor_button.setStyleSheet(color_name)
        self.ui.special_row_bgcolor_button.setText("")

        self.init_controls()

    def init_controls(self):
        self.ui.caption_bgcolor_button.clicked.connect(self.set_caption_bgcolor)
        self.ui.special_row_bgcolor_button.clicked.connect(self.set_special_row_bgcolor)
        self.settings = QtCore.QSettings("calculator_settings")
        self.ui.save_button.clicked.connect(self.save_settings)

    def set_caption_bgcolor(self):
        col = QColorDialog.getColor()
        self.caption_bgcolor = col.name()
        color_name = "QPushButton { background-color: color_name }".replace(
            "color_name", col.name()
        )

        if col.isValid():
            self.ui.caption_bgcolor_button.setStyleSheet(color_name)

    def set_special_row_bgcolor(self):
        col = QColorDialog.getColor()
        self.special_row_bgcolor = col.name()
        color_name = "QPushButton { background-color: color_name }".replace(
            "color_name", col.name()
        )

        if col.isValid():
            self.ui.special_row_bgcolor_button.setStyleSheet(color_name)

    def save_settings(self):
        self.settings.setValue("caption_bgcolor", self.caption_bgcolor)
        self.settings.setValue("special_row_bgcolor", self.special_row_bgcolor)
        self.close()


class CalculatorWindow(QtWidgets.QMainWindow):  
    
    # data for html table
    data = None
    # data without format (decimal separator, percent, dollar,...)
    tmp_data = None
    
    general_analysis_and_results = None
    
    # property info
    address = ''
    city = ''
    state = ''
    zip_code = 0
    prior_year_taxes = 0
    landlord_insurance = 0
    property_images = []
    
    # purchase information
    asking_price = 0
    rate = 0
    term = 0
    present_value = 0
    arv = 0
    loan_amount_auto = 0
    int_rate = 0
    downpayment = 0
    downpayment_dollar = 0
    purchase_price = 0
    rehab_budget = 0
    closing_costs = 0
    finance_rehab_logical = 'Yes'
    emergency_fund = 0
    term_years = 0
    
    # fixed expenses
    total_fixed_expense = 0
    electric = 0
    WandS = 0
    PMI = 0
    garbage = 0
    HOA = 0
    insurance = 0
    taxes = 0
    other = 0
    
    # variable expenses
    total_variable_expense = 0
    vacancy = 0
    vacancy_dollar = 0
    rep_and_main = 0
    rep_and_main_dollar = 0
    cap_ex = 0
    cap_ex_dollar = 0
    other_income = 0
    management = 0
    management_dollar = 0

    # income
    total_income_monthly = 0
    tot_monthly_income = 0
    ave_rent = 0
    rental_income_monthly = 0
    num_units = 0
    
    # assumptions 
    exp_appreciation = 0
    rent_appreciation = 0
    selling_costs = 0
    prop_appreciation = 0
    
    
    def __init__(self):
        super(CalculatorWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_signals()
        self.init_validators()
        self.init_fake_values() # TODO: remove
        
        # init data structures
        self.data = defaultdict(list)        
        self.tmp_data = defaultdict(list)        
        
        self.auto_calculations()
        self.update_total_exp_auto()
        
    def auto_calculations(self):
        self.auto_loan_amount()
        
    def init_fake_values(self):
        """ TODO: delete after testing"""
        
        self.address = '123 SFI Dr.'
        self.city = 'Anytown'
        self.state = 'AK'
        self.zip_code = 12340
        self.prior_year_taxes = 850
        self.landlord_insurance = 750
        self.property_images = []
        
        self.asking_price = 120000
        self.rate = 4.5 / 100
        self.term = 234
        self.present_value = 4000
        self.arv = 1
        self.loan_amount_auto = 0
        self.int_rate = 4.5 / 100
        self.downpaymeinit_validatorsnt = 20
        self.downpayment_dollar = 40000
        self.purchase_price = 200000
        self.rehab_budget = 50000
        self.closing_costs = 3500
        self.finance_rehab_logical = 'Yes'
        self.emergency_fund = 5000
        self.term_years = 30
        
        # fixed expenses
        self.total_fixed_expense = 253.33
        self.electric = 30
        self.WandS = 10
        self.PMI = 20
        self.garbage = 20
        self.HOA = 20
        self.insurance = 20
        self.taxes = 20
        self.other = 20
        
        # variable expenses
        self.total_variable_expense = 1200
        self.vacancy = 210
        self.vacancy_dollar = 20
        self.rep_and_main = 10
        self.rep_and_main_dollar = 110
        self.cap_ex = 30
        self.cap_ex_dollar = 4
        self.other_income = 5
        self.management = 6
        self.management_dollar = 60

        # income
        self.total_income_monthly = 1300
        self.tot_monthly_income = 1300
        self.ave_rent = 1200
        self.rental_income_monthly = 120
        self.num_units = 1
        
        # assumptions 
        self.exp_appreciation = 20
        self.rent_appreciation = 30
        self.selling_costs = 40
        self.prop_appreciation = 50        
        
    def validate_values(self):
        try:
            # property info
            self.address = self.ui.address_input.text()
            self.city = self.ui.city_input.text()
            self.state = self.ui.state_input.currentText()            
            self.zip_code = int(self.ui.zip_input.text())
            self.prior_year_taxes = float(self.ui.taxes_input.text())
            self.landlord_insurance = float(self.ui.annual_insurance_input.text())
            
            self.rate = self.ui.int_rate_input_2.value()

            # purchase information tab inputs
            self.asking_price = float(self.ui.asking_price_input.text())
            self.purchase_price = float(self.ui.purchase_price_input.text())
            self.finance_rehab_logical = self.ui.fin_rehab_logical.currentText()
            self.rehab_budget = float(self.ui.rehab_budget_input.text())
            self.arv = float(self.ui.arv_input.text())
            self.closing_costs = float(self.ui.closing_costs_input.text())
            self.emergency_fund = float(self.ui.emerg_fund_input.text())
            self.downpayment = float(self.ui.downpayment_percentage_input_2.value())
            self.downpayment_dollar = float(self.ui.dp_dollar_auto_2.text())
            self.loan_amount = float(self.ui.loan_amount_auto_2.text())
            self.term = self.ui.term_input_2.value()
            
            # income tab inputs
            self.num_units = float(self.ui.num_units_input.value())
            self.ave_rent = float(self.ui.ave_rent_input.text())
            self.tot_monthly_income = float(self.ui.tot_rent_month_auto.text())
            self.other_income = float(self.ui.other_income_month_input.text())
            self.total_income_monthly = float(self.ui.tot_income_month_auto.text())
            
            # expenses tab inputs
            self.total_fixed_expense = float(self.ui.tot_fixed_exp_auto.text())
            self.electric = float(self.ui.electric_input.text())
            self.WandS = float(self.ui.w_and_s_input.text())
            self.PMI = float(self.ui.pmi_input.text())
            self.garbage = float(self.ui.garbage_input.text())
            self.HOA = float(self.ui.hoa_input.text())
            self.taxes = float(self.ui.monthly_taxes_auto.text())
            self.insurance = float(self.ui.insurance_auto.text())
            self.other = float(self.ui.other_input.text())
            self.total_variable_expense = float(self.ui.tot_var_exp_auto.text())
            self.rep_and_main = float(self.ui.r_and_m_input.text())
            self.rep_and_main_dollar= float(self.ui.r_and_m_auto.text())
            self.rep_and_main_dollar= float(self.ui.r_and_m_auto.text())
            self.cap_ex = float(self.ui.cap_ex_input.text())
            self.cap_ex_dollar = float(self.ui.cap_ex_auto.text())
            self.vacancy = float(self.ui.vacancy_auto.text())
            self.vacancy_dollar = float(self.ui.vacancy_input.text())
            self.management = float(self.ui.manag_input.text())
            self.management_dollar = float(self.ui.manag_auto.text())
            
            # Assumptions tab inputs
            self.rent_appreciation = float(self.ui.rent_appreciation_input.text())
            self.exp_appreciation = float(self.ui.exp_appreciation_input.text())
            self.prop_appreciation = float(self.ui.prop_appreciation_input.text())
            self.selling_costs = float(self.ui.selling_costs_input.text())
            
        except Exception as ex:
            _, _, tb = sys.exc_info()
            self.show_message(message='Validate values', 
                              details=f'Line: {tb.tb_lineno},\n {str(ex)}', 
                              msg_type='warning')
            return False
        
        return True

    def init_signals(self):
        self.ui.Generate_Report.clicked.connect(self.generate_report)
        self.ui.actionSettings.triggered.connect(self.settings_window)
                
        # auto fields
        self.ui.r_and_m_input.editingFinished.connect(
            self.repair_and_maintenance_changed
        )
        self.ui.cap_ex_input.editingFinished.connect(self.cap_ex_changed)
        self.ui.ave_rent_input.editingFinished.connect(self.ave_rent_changed)
        self.ui.other_income_month_input.editingFinished.connect(
            self.other_income_month_changed
        )
        self.ui.int_rate_input_2.valueChanged.connect(self.interest_rate_changed)
        self.ui.term_input_2.valueChanged.connect(self.term_years_changed)
        # calculate downpayment $ when downpayment % is changed
        self.ui.downpayment_percentage_input_2.valueChanged.connect(self.downpayment_percent_changed)        
        # expenses tab auto fields
        self.ui.vacancy_input.textChanged.connect(self.vacancy_input_changed)       
        self.ui.cap_ex_input.textChanged.connect(self.cap_ex_input_changed)       
        self.ui.r_and_m_input.textChanged.connect(self.r_and_m_input_changed)       
        self.ui.manag_input.textChanged.connect(self.manag_input_changed)       
        self.ui.electric_input.textChanged.connect(self.electric_input_changed)       
        self.ui.w_and_s_input.textChanged.connect(self.w_and_s_input_changed)       
        self.ui.pmi_input.textChanged.connect(self.pmi_input_changed)       
        self.ui.garbage_input.textChanged.connect(self.garbage_input_changed)       
        self.ui.hoa_input.textChanged.connect(self.hoa_input_changed)       
        self.ui.other_input.textChanged.connect(self.other_input_changed)
        # property
        self.ui.annual_insurance_input.textChanged.connect(self.annual_insurance_input_changed)
        self.ui.taxes_input.textChanged.connect(self.taxes_input_changed)

    def init_validators(self):
        # purchase information tab
        self.ui.asking_price_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.purchase_price_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.rehab_budget_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.arv_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.closing_costs_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.emerg_fund_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        # income tab
        self.ui.ave_rent_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.other_income_month_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        # expenses tab
        self.ui.electric_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.w_and_s_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.hoa_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.other_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.r_and_m_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.cap_ex_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.vacancy_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.manag_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        # assumptions tab
        self.ui.rent_appreciation_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.exp_appreciation_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.prop_appreciation_input.setValidator(QDoubleValidator(999999999, -999999999, 8))
        self.ui.selling_costs_input.setValidator(QDoubleValidator(999999999, -999999999, 8))

    def settings_window(self):
        settings_dialog = SettingsWindow(self)
        settings_dialog.show()

    def taxes_input_changed(self):
        try:
            self.taxes = float(self.ui.taxes_input.text()) / 12            
        except ValueError:
            self.ui.taxes_input.setText("0")
            return
        
        self.ui.monthly_taxes_auto.setText(str(self.taxes))
        self.update_total_exp_auto()
        
    def annual_insurance_input_changed(self):
        try:
            self.insurance = float(self.ui.annual_insurance_input.text()) / 12            
        except ValueError:
            self.ui.insurance_auto.setText("0")
            return
        
        self.ui.insurance_auto.setText(str(self.insurance))
        self.update_total_exp_auto()
    
    def other_input_changed(self):
        try:
            self.other = float(self.ui.other_input.text())
        except ValueError:
            self.ui.other_input.setText("0")
        
        self.update_total_exp_auto()

    def garbage_input_changed(self):
        try:
            self.garbage = float(self.ui.garbage_input.text())
        except ValueError:
            self.ui.garbage_input.setText("0")
        
        self.update_total_exp_auto()

    def hoa_input_changed(self):
        try:
            self.HOA = float(self.ui.hoa_input.text())
        except ValueError:
            self.ui.hoa_input.setText("0")
        
        self.update_total_exp_auto()

    def pmi_input_changed(self):
        try:
            self.PMI = float(self.ui.pmi_input.text())
        except ValueError:
            self.ui.pmi_input.setText("0")
        
        self.update_total_exp_auto()

    def w_and_s_input_changed(self):
        try:
            self.WandS = float(self.ui.w_and_s_input.text())
        except ValueError:
            self.ui.w_and_s_input.setText("0")
        
        self.update_total_exp_auto()
        
    def electric_input_changed(self):
        try:
            self.electric = float(self.ui.electric_input.text())
        except ValueError:
            self.ui.electric_input.setText("0")
        
        self.update_total_exp_auto()
        
    def manag_input_changed(self):
        try:
            self.management = float(self.ui.manag_input.text())
        except ValueError:
            self.ui.manag_auto.setText("0")
            self.ui.tot_fixed_exp_auto.setText("0")
            self.ui.tot_var_exp_auto.setText("0")            
            return
        
        self.management_dollar = REI_Calculations.calculate_dollar_amount(
            self.total_income_monthly,
            self.management
        )
        self.ui.manag_auto.setText(str(self.management))
        
    def r_and_m_input_changed(self):
        """Repair and maintenance"""
        try:
            self.rep_and_main = float(self.ui.r_and_m_input.text())
        except ValueError:
            self.ui.r_and_m_auto.setText("0")
            #self.ui.tot_fixed_exp_auto.setText("0")
            self.ui.tot_var_exp_auto.setText("0")
            return
        
        self.rep_and_main_dollar = REI_Calculations.calculate_dollar_amount(
            self.total_income_monthly,
            self.rep_and_main
        )
        self.ui.r_and_m_auto.setText(str(self.rep_and_main_dollar))
        # update total (fixed, variable) expenses
        self.update_total_exp_auto()
        
    def update_total_exp_auto(self):
        """Update total expenses (fixed and variable)
        """
        self.total_variable_expense, _ = REI_Calculations.variable_expenses_monthly(
            self.total_income_monthly,
            self.rep_and_main_dollar,
            self.cap_ex_dollar,
            self.vacancy_dollar,
            self.management_dollar
        )
        self.ui.tot_var_exp_auto.setText(str(self.total_variable_expense))
        
        self.total_fixed_expense, _ = REI_Calculations.fixed_expenses_monthly(
            self.electric, self.WandS, self.PMI,
            self.garbage, self.HOA, self.insurance,
            self.taxes, self.other
        )
        self.ui.tot_fixed_exp_auto.setText(str(self.total_fixed_expense))
        
    def cap_ex_input_changed(self):
        try:
            self.cap_ex = float(self.ui.cap_ex_input.text())
        except ValueError:
            self.ui.cap_ex_auto.setText("0")
            return
        
        self.cap_ex_dollar = REI_Calculations.calculate_dollar_amount(
            self.total_income_monthly,
            self.cap_ex
        )
        self.ui.cap_ex_auto.setText(str(self.cap_ex_dollar))
    
    def vacancy_input_changed(self):
        try:
            self.vacancy = float(self.ui.vacancy_input.text())
        except ValueError:
            self.ui.vacancy_auto.setText("0")
            return
        
        self.vacancy_dollar = REI_Calculations.calculate_dollar_amount(
            self.total_income_monthly, 
            self.vacancy
        )
        self.ui.vacancy_auto.setText(str(self.vacancy_dollar))
    
    def other_income_month_changed(self):
        try:
            self.other_income = float(
                self.ui.other_income_month_input.text()
                .strip()
                .replace("%", "")
                .replace(",", ".")
            )
        except Exception as ex:
            self.show_message("Wrong value for other income month", msg_type="warning")

    def downpayment_percent_changed(self, value):
        self.downpayment = value
        self.downpayment_dollar = REI_Calculations.calculate_dollar_amount(
            self.purchase_price, self.downpayment
        )
        self.ui.dp_dollar_auto_2.setText(str(self.downpayment_dollar))                    
        # recalculate loan
        self.auto_loan_amount()        
        
    def auto_loan_amount(self):
        # loan amount auto calculation        
        payment = REI_Calculations.full_loan_amount(
            self.purchase_price, 
            self.finance_rehab_logical, 
            self.rehab_budget, 
            self.downpayment_dollar / 100
        )
        self.loan_amount_auto = payment
        self.ui.loan_amount_auto_2.setText(str(self.loan_amount_auto))
        
    def interest_rate_changed(self, value):
        self.int_rate = value        
        #self.auto_loan_amount()

    def term_years_changed(self, value):
        self.term = value        
        #self.auto_loan_amount()
        
    def ave_rent_changed(self):
        try:
            self.ave_rent = float(
                self.ui.ave_rent_input.text().strip().replace("%", "").replace(",", ".")
            )
        except Exception as ex:
            print(ex)
            self.show_message(
                "Wrong value for average rent per unit", msg_type="warning"
            )

    def repair_and_maintenance_changed(self):
        try:
            self.rep_and_main = float(
                self.ui.r_and_m_input.text().strip().replace("%", "").replace(",", ".")
            )
        except Exception as ex:
            self.show_message(
                message="Wrong value for repair and maintenance", 
                msg_type="warning"
            )

    def cap_ex_changed(self):
        try:
            self.cap_ex = float(
                self.ui.cap_ex_input.text().strip().replace("%", "").replace(",", ".")
            )
        except Exception as ex:
            self.show_message(message="Wrong value for cap. ex", 
                              msg_type="warning")

    def generate_report(self):
        if not self.validate_values():
            return
        self.init_fake_values()
        
        self.run_calculations()
        if not self.data:
            print("No data after calculations")
            return
        
        # dataframe for plotting three totals
        plot_data = DataFrame.from_dict(self.tmp_data).iloc[[0,1,7], :]
        print(plot_data)
                    
        data_output.generate_report(self.general_analysis_and_results, self.data, plot_data)
        

    def show_message(self, message, details=None, msg_type="info"):
        msg = QMessageBox()
        if msg_type == "warning":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.setText(message)
        msg.setWindowTitle("Message")
        if details:
            msg.setInformativeText(details)
            msg.setDetailedText(details)

        msg.exec_()

    def run_calculations(self):
        ## Initially we just need to calculate the 12 key figures.
        ## Will then build a loop for the Pro forma statement.

        # Begin by calculating the monthly payment of the loan
        try:
            print(f'rate: {self.rate} term: {self.term}  present value: {self.present_value}')
            payment = REI_Calculations.loan_payment(self.rate, self.term, self.present_value)
        except Exception as ex:
            _, _, tb = sys.exc_info()
            self.show_message(message='Run calculations', 
                              details=f'run_calculations(), loan_payment: Line: {tb.tb_lineno},\n {str(ex)}', 
                              msg_type='warning')            
            return False

        # Each item that is to be showcased will have a number before it.
        # only 8 are being calculated here.  There are an additional 4
        #   - Purchase Price (taken from GUI input)
        #   - Monthly Income (taken from GUI input)
        #   - Monthly Expense ( sum(fixed_monthly, var_monthly) )
        # The desired order for the 12 are to be as follows:
        #
        # cash_2_close  Purch. Price   Monthly Income
        # Monthly Exp.  Monthly CF     50% Rule
        # NOI           NIAF           CoCR
        # Cap Rate      1% Rule        Gross Rent Mult.

        # Calculate the fixed and variable expenses
        fixed_monthly, fixed_yearly = REI_Calculations.fixed_expenses_monthly(
            self.electric, self.WandS, self.PMI, 
            self.garbage, self.HOA, self.insurance, 
            self.taxes, self.other
        )

        var_monthly, var_yearly = REI_Calculations.variable_expenses_monthly(
            self.total_income_monthly, self.vacancy, self.rep_and_main, 
            self.cap_ex, self.management
        )

        # 1 Calculate NOI
        NOI = REI_Calculations.NOI_yearly(
            self.total_income_monthly * 12, fixed_yearly, var_yearly
        )


        # 2,3 Calculate Monthly and yearly NIAF or monthly cash flows
        cf_monthly = REI_Calculations.cash_flow_monthly(
            self.total_income_monthly, payment, fixed_monthly, var_monthly
        )
        NIAF = REI_Calculations.NIAF_yearly(NOI, payment)

        # 4 Calculate the cash to close
        cash_2_close = REI_Calculations.cash_to_close(
            self.downpayment,
            self.closing_costs,
            self.emergency_fund,
            self.rehab_budget,
            self.finance_rehab_logical,
        )

        # 5 Calculate Cash on Cash Return (CoCR)
        CoCR = REI_Calculations.cash_on_cash_return(NIAF, cash_2_close)

        # 6 Calculate the cap rate
        try:
            capRate = REI_Calculations.cap_rate(NOI, self.purchase_price, self.rehab_budget, self.closing_costs)
        except Exception as ex:
            _, _, tb = sys.exc_info()
            self.show_message(message='Run calculations', 
                              details=f'run_calculations(), cap_rate: Line: {tb.tb_lineno},\n {str(ex)}', 
                              msg_type='warning')            
            return False
        
        # 7 Calculate Gross Rent Multiplier
        try:
            GRM = REI_Calculations.gross_rent_mult(
                self.purchase_price, self.rehab_budget, self.total_income_monthly
            )
        except Exception as ex:
            _, _, tb = sys.exc_info()
            self.show_message(message='Run calculations', 
                              details=f'run_calculations(), gross_rent_mult: Line: {tb.tb_lineno},\n {str(ex)}', 
                              msg_type='warning')            
            return False
        
        # 8,9 Calculate the 1 and 50 percent rules
        one_perc = REI_Calculations.one_perc_rule(
            self.purchase_price, self.rehab_budget, self.total_income_monthly
        )
        fifty_perc = REI_Calculations.fifty_perc_rule(
            fixed_monthly, var_monthly, self.total_income_monthly
        )
               
        self.general_analysis_and_results = [
            [ 
                '${:0,.2f}'.format(cash_2_close),  
                '${:0,.2f}'.format(self.purchase_price), 
                '${:0,.2f}'.format(self.tot_monthly_income)
            ], 
            [ 
                '${:0,.2f}'.format(var_monthly), 
                '${:0,.2f}'.format(cf_monthly), 
                '{:0,.2f}%'.format(one_perc)
            ], 
            [ 
                '${:0,.2f}'.format(NOI),  
                '${:0,.2f}'.format(NIAF), 
                '{:0,.2f}%'.format(CoCR)
            ],
            [ 
                '{:0,.2f}%'.format(capRate), 
                '{:0,.2f}%'.format(fifty_perc),  
                '{:0,.2f}'.format(GRM)
            ]
        ]
            
        ## Will need to store this data now as some of it may be overwritten
        # during the pro forma construction

        ## Now we begin the loop for ten years.  I will define a var here
        # because in the future I may make this adjustable for the number
        # of years to do the pro forma for

        ## Pro forma begins
        # Set initial values
        cum_NIAF = 0
        cum_CoCR = 0
        length_yrs = range(1, 10)

        for year_index in length_yrs:
            # Everything will be on a yearly scale and we may calculate some
            # variables two time for this first year
            
            # Calculate total annual income for each year
            tot_income_annual = REI_Calculations.future_value(
                self.rent_appreciation, year_index - 1, 0, self.tot_monthly_income
            )

            # Calculate total fixed expenses for each year
            fixed_yearly = REI_Calculations.future_value(
                self.exp_appreciation, year_index - 1, 0, fixed_monthly * 12
            )

            # Calculate total variable expenses for each year
            var_yearly = tot_income_annual * sum(
                [self.rep_and_main, self.cap_ex, self.vacancy, self.management]
            )

            # Calculate Total Expenses
            tot_expense_yearly = sum([fixed_yearly, var_yearly])

            # Calculate NOI
            NOI = REI_Calculations.NOI_yearly(
                tot_income_annual, fixed_yearly, var_yearly
            )

            # Calculate Debt service
            if self.term < year_index:
                payment = 0
            payment_annual = payment * 12

            # Calculate NIAF
            NIAF = REI_Calculations.NIAF_yearly(NOI, payment)

            # Calculate Property Value
            prop_value = REI_Calculations.future_value(
                self.prop_appreciation, year_index - 1, 0, self.arv
            )

            # Calculate Cash on Cash Return
            CoCR = REI_Calculations.cash_on_cash_return(NIAF, cash_2_close)

            # Calculate cumulative CoCR
            cum_CoCR = cum_CoCR + CoCR

            # Calculate cumulative NIAF
            cum_NIAF = cum_NIAF + NIAF

            # Calculate future loan balance
            loan_balance = REI_Calculations.future_value(
                self.int_rate / 12, year_index * 12, payment, self.loan_amount_auto
            )
            # Calculate total equity owned by investor
            tot_equity = REI_Calculations.future_equity(prop_value, loan_balance)

            # Calculate percent of equity owned by the investor
            equity_perc = tot_equity / prop_value

            # Calculate ROI
            ROI = REI_Calculations.return_on_investment(
                tot_equity, cum_NIAF, cash_2_close
            )

            # Calculate profit if sold
            total_profit_sold = REI_Calculations.tot_profit_sold(
                prop_value, self.selling_costs, self.loan_amount_auto, cash_2_close, 
                cum_NIAF, self.downpayment_dollar
            )

            # Calculate the compounded annual growth rate (CAGR) if sold
            CAGR = REI_Calculations.compound_annual_growth_rate(
                total_profit_sold, year_index, cash_2_close
            )
            
            self.tmp_data[f'Year_{year_index}'] = [
                tot_income_annual, tot_expense_yearly, fixed_yearly,
                var_yearly, NOI, 0,
                0, NIAF, prop_value,
                CoCR, cum_CoCR, tot_equity,
                equity_perc, ROI, total_profit_sold,
                CAGR
            ]
            
            self.tmp_data[f'Year_{year_index}'] = [randint(0, 1200) for _ in range(16)]
            
            tot_income_annual = '{:0,.2f}'.format(tot_income_annual)
            tot_expense_yearly = '{:0,.2f}'.format(tot_expense_yearly)
            fixed_yearly = '{:0,.2f}'.format(fixed_yearly)
            var_yearly = '{:0,.2f}'.format(var_yearly)
            NOI = '{:0,.2f}'.format(NOI)
            NIAF = '{:0,.2f}'.format(NIAF)
            prop_value = '{:0,.2f}'.format(prop_value)
            tot_equity = '{:0,.2f}'.format(tot_equity)
            ROI = '{:0,.2f}'.format(ROI)
            total_profit_sold= '{:0,.2f}'.format(total_profit_sold)
            equity_perc = '{:0,.2f}'.format(equity_perc)
            #CAGR= '{:0,.2f}'.format(CAGR)
            
            
            self.data[f'Year_{year_index}'] = [
                f'${tot_income_annual}', f'${tot_expense_yearly}', f'${fixed_yearly}',
                f'${var_yearly}', f'${NOI}', '0.0%',
                '$0', f'${NIAF}', f'${prop_value}',
                f'{CoCR}%' ,f'{cum_CoCR}%', f'${tot_equity}',
                f'{equity_perc}%', f'{ROI}%', f'${total_profit_sold}',
                f'{CAGR}%'
            ]



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = CalculatorWindow()
    application.show()
    sys.exit(app.exec())
