from cmath import phase
import numpy
import Gnuplot


def extract_data_sweep(save_dic, current_channel, initial_spec, step, spectrum):
    spectrum = spectrum[0]
    function_name = 'extract_data_sweep'
    if current_channel == 0:
        save_dic[function_name] = [spectrum[initial_spec]]
        return

    channel = initial_spec + current_channel*step

    if channel >= len(spectrum):
        raise Exception('Asking for a channel thats out of possible range.')

    save_dic[function_name].append(spectrum[channel])

def fase_difference_amplitudes(save_dic, current_channel, initial_spec, step, spectrum, spectrum_ref):
    spectrum = spectrum[0]
    spectrum_ref = spectrum_ref[0]
    function_name = 'fase_difference_amplitudes'
    if current_channel == 0:
        a1 = spectrum[initial_spec]
        a2 = spectrum_ref[initial_spec]
        angle = phase(a1*a2.conjugate())

        save_dic[function_name] = [(abs(a1),abs(a2),angle)]
        save_dic['angle'] = [angle,]

        g3 = Gnuplot.Gnuplot(debug=0)
        g3.clear()
        g3.title('Phase (degree)')
        g3.xlabel('Channel #')
        g3.ylabel('Degrees')
        g3('set style data points')
        # g3('set terminal wxt size 500,300')
        g3('set yrange [-6:6]')
        g3('set xrange [0:256]')
        g3('set ytics 0.35')
        g3('set xtics 16')
        g3('set grid y')
        g3('set grid x')

        save_dic['plot'] = g3.plot
        return

    channel = initial_spec + current_channel*step

    if channel >= len(spectrum):
        raise Exception('Asking for a channel thats out of possible range.')

    channel = initial_spec + current_channel*step

    a1 = spectrum[channel]
    a2 = spectrum_ref[channel]

    angle = phase(a1*a2.conjugate())

    print current_channel, angle * 180/3.141592, 'angle'

    save_dic[function_name].append((abs(a1),abs(a2),angle))
    save_dic['angle'].append(angle)

    save_dic['plot'](save_dic['angle'])

def fase_difference_amplitudes_ratio(save_dic, current_channel, initial_spec, step, spectrum, spectrum_ref):
    spectrum = spectrum[0]
    spectrum_ref = spectrum_ref[0]
    function_name = 'fase_difference_amplitudes'
    if current_channel == 0:
        a1 = abs(spectrum[initial_spec])
        a2 = abs(spectrum_ref[initial_spec])
        ratio = 0 if a2==0 else a1/a2
        angle = phase(a1*a2.conjugate())

        save_dic[function_name] = [(ratio,angle)]
        return

    channel = initial_spec + current_channel*step

    if channel >= len(spectrum):
        raise Exception('Asking for a channel thats out of possible range.')

    channel = initial_spec + current_channel*step

    a1 = abs(spectrum[initial_spec])
    a2 = abs(spectrum_ref[initial_spec])
    ratio = 0 if a2==0 else a1/a2
    angle = phase(a1*a2.conjugate())

    save_dic[function_name].append((ratio,angle))