import SUNXI_GPIO as GPIO

'''http://docs.cubieboard.org/tutorials/common/using_python_program_control_gpios'''


class Outputs():

    '''
    outputs -> format [{'name':'R1','value':'1'}, ..., {}]
    '''
    def __init__(self, outputs=None):
        self.R1 = GPIO.PD0
        self.R2 = GPIO.PD1
        self.R3 = GPIO.PD2
        self.R4 = GPIO.PD3
        self.outputs = {'R1': {'pin': GPIO.PD0, 'value': GPIO.LOW}, 'R2': {'pin': GPIO.PD1, 'value': GPIO.LOW}, 'R3': {'pin': GPIO.PD2, 'value': GPIO.LOW}, 'R4': {'pin': GPIO.PD3, 'value': GPIO.LOW}}
        if outputs:
            for output in outputs:
                value = GPIO.LOW
                if output['value'] in ['1', True, 'True']:
                    value = GPIO.HIGH
                self.outputs[output['name']]['value'] = value
        self.values = [0, 0, 0, 0]
        GPIO.init()
        #outputs initialization
        self.init_ouputs()

    def init_ouputs(self):
        for name, output in self.outputs.iteritems():
            GPIO.setcfg(output['pin'], GPIO.OUT)
            GPIO.output(output['pin'], output['value'])

    def set(self, output, enable):
        if output in self.outputs:
            if enable in ['on', '1', 1, 'True', True]:
                if self.outputs[output]['value'] != '%s' % GPIO.HIGH:
                    print "Outputs set called %s:%s" % (self.outputs[output]['pin'], GPIO.HIGH)
                    self.outputs[output]['value'] = '%s' % GPIO.HIGH
                    GPIO.output(self.outputs[output]['pin'], GPIO.HIGH)
                    print self.outputs[output]['value']
                    return True
            else:
                if self.outputs[output]['value'] != '%s' % GPIO.LOW:
                    print "Outputs set called %s:%s" % (self.outputs[output]['pin'], GPIO.LOW)
                    self.outputs[output]['value'] = '%s' % GPIO.LOW
                    GPIO.output(self.outputs[output]['pin'], GPIO.LOW)
                    return True
        return False
