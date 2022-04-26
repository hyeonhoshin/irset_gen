# Program for Data generator.

## To-do
- [x] Check the accuracy of FPS.py. (No prob confirmed.)
- [x] Booting time optimization 2.3890s -> 0.3088s
- [x] Delete unmeaningful subfolder 'unified'.
- [x] Backup all the files which exist in the prior to our unified folder.
- [x] Check the pre-made files function and delete useless ones.
- [ ] Add Software defined ISP
- [ ] Add manual ISP mode by argument

## Bug fix.
- Namjo fixed the synchronization issue between high-res and low-res video.

## Function description of old files

- main.py : 기본 파일. 승우씨가 기록의 편의성을 개선해둠.
- main_n.py : main.py에서 CDS를 끔.
- main_night.py : CDS를 끈 채로 횟수 증가 -> sampling 수를 증가시켜서 낮은 SNR을 개선코자한듯.
- main2,3.py : hir captureing이 꺼져 있고, 내용은 동일하지만 다른 FPS.py을 호출하게 되어있음. Multi-angle 촬영을 위한 파일인듯.
- main_CG0.5_Iref1.py : Total Gain : 0.49,  GAIN factor : 0.49, Relative ADC Gain from I_ref = 1
- main_CG2_Iref4.py : Total Gain : 0.51, GAIN factor : 2.04, Relative ADC Gain from l_ref = 1/4

## Experiment results for HR IR optimization
- 평소 : 약 35~39fps
- LR drawer 제거 : 약 45fps.
- LR drawer 제거 + Save 함수 제거 : 47fps.
- HR drawer만 제거 : 약 40.1fps.
