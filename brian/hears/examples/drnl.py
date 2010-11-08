
'''
http://www.freesound.org
Implementation of the dual resonance nonlinear (DRNL) filter.
The parameters are those fitted for human
from Lopez-Paveda, E. and Meddis, R.., A human nonlinear cochlear filterbank, JASA 2001

The entire pathway consists of the sum of a linear and a nonlinear pathway

The linear path consists of a bandpass function (second order gammatone), a low pass function,
and a gain/attenuation factor, g, in a cascade

The nonlinear path is  a cascade consisting of a bandpass function, a
compression function, a second bandpass function, and a low
pass function, in that order.

'''

from brian import *
from time import  time


from brian.hears import*
from brian.hears import filtering
filtering.use_gpu = False
#set_global_preferences(useweave=True)

samplerate=40*kHz

simulation_duration=50*ms
dBlevel=50  # dB level in rms dB SPL

samplerate,sound=get_wav('/home/bertrand/Data/Toolboxes/AIM2006-1.40/Sounds/aimmat.wav')
sound=Sound(sound,samplerate)
#sound.atintensity(dBlevel)
print 'fs=',samplerate,'duration=',len(sound)/samplerate
simulation_duration=len(sound)/samplerate
defaultclock.dt = 1/samplerate
#plot(sound)
#show()
#exit()

#sound = whitenoise(simulation_duration,samplerate,dB=dBlevel).ramp()

nbr_center_frequencies=50
center_frequencies=erbspace(20*Hz,1000*Hz, nbr_center_frequencies) 

#### middle ear processing ####
f_cut_off1=25*kHz/ ( ( 10**(0.1*10)-1)**(1.0/(2.0*2))) #Find the butterworth natural frequency W0 from the lower and higher cutt off 
f_cut_off2=30*kHz/ ( ( 10**(0.1*10)-1)**(1.0/(2.0*2)))
lp_l1=ButterworthFilterbank(samplerate, 1, 2,f_cut_off1, btype='low')
lp_l2=ButterworthFilterbank(samplerate, 1, 3,f_cut_off2, btype='low')
#middle_ear=FilterbankChain([lp_l1,lp_l2])
middle_ear=DoNothingFilterbank(samplerate, 1)

#### conversion from pressure (Pascal) in stapes velocity (in m/s)
stape_scale=0.00014
stape_scale=1./0.00014
stapes_fun=lambda x:x*stape_scale
stapes_conv=FunctionFilterbank(samplerate, 1, stapes_fun)


#### Linear Pathway ####

#linear gain
g=10**(4.20405-0.47909*log10(center_frequencies))
func_gain=lambda x:g*x
gain=FunctionFilterbank(samplerate, nbr_center_frequencies, func_gain)

#bandpass filter (second order  gammatone filter)
center_frequencies_linear=10**(-0.06762+1.01679*log10(center_frequencies))
bandwidth_linear=10**(0.03728+0.78563*log10(center_frequencies))
order_linear=2
bandpass_linear =MeddisGammatoneFilterbank(samplerate, center_frequencies_linear, order_linear, bandwidth_linear)

#low pass filter(cascade of 4 second order lowpass butterworth filters)
cutoff_frequencies_linear=center_frequencies_linear
order_lowpass_linear=2
lp_l=ButterworthFilterbank(samplerate, nbr_center_frequencies, order_lowpass_linear, cutoff_frequencies_linear, btype='low')
lowpass_linear=CascadeFilterbank(lp_l,4)

#linear pathway
linear_path=FilterbankChain([gain,bandpass_linear,lowpass_linear])


#### Nonlinear Pathway ####

#bandpass filter (third order gammatone filters)
center_frequencies_nonlinear=10**(-0.05252+1.0165*log10(center_frequencies))
bandwidth_nonlinear=10**(-0.03193+0.77426*log10(center_frequencies))
order_nonlinear=3
bandpass_nonlinear1=MeddisGammatoneFilterbank(samplerate, center_frequencies_nonlinear, order_nonlinear, bandwidth_nonlinear)

#compression (linear at low level, compress at high level)
a=10**(1.40298+0.81916*log10(center_frequencies))  #linear gain
b=10**(1.61912-0.81867*log10(center_frequencies))  
v=0.25  #compression exponent
func_compression=lambda x:sign(x)*minimum(a*abs(x),b*abs(x)**v)
compression=FunctionFilterbank(samplerate, nbr_center_frequencies, func_compression)

#bandpass filter (third order gammatone filters)
bandpass_nonlinear2=MeddisGammatoneFilterbank(samplerate, center_frequencies_nonlinear, order_nonlinear, bandwidth_nonlinear)

#low pass filter
cutoff_frequencies_nonlinear=center_frequencies_nonlinear
order_lowpass_nonlinear=2
lp_nl=ButterworthFilterbank(samplerate, nbr_center_frequencies, order_lowpass_nonlinear, cutoff_frequencies_nonlinear, btype='low')
lowpass_nonlinear=CascadeFilterbank(lp_nl,4)

#nonlinear pathway
nonlinear_path=FilterbankChain([bandpass_nonlinear1,compression,bandpass_nonlinear2,lowpass_nonlinear])


#### adding the two pathways together ####
dnrl_filter=linear_path+nonlinear_path

#### chaining everything ####
filters_1dpath=FilterbankChain([middle_ear,stapes_conv])
processing_1dpath= FilterbankGroup(filters_1dpath, sound)     #1d fu=ilter chain of middle ear

dnrl= FilterbankGroup(dnrl_filter, processing_1dpath.output)

#dnrl= FilterbankGroup(dnrl_filter, sound)
dnrl_monitor = StateMonitor(dnrl, 'output', record=True)

t1=time()
run(simulation_duration)
print 'the simulation took %f sec to run' %(time()-t1)

time_axis=dnrl_monitor.times

figure()

imshow(flipud(dnrl_monitor.getvalues()),aspect='auto')

#for ifrequency in range((nbr_center_frequencies)):
#    subplot(nbr_center_frequencies,1,ifrequency+1)
#    plot(time_axis*1000,dnrl_monitor [ifrequency])
#    xlabel('(ms)')
    
show()


