# Airflow, MLFlow를 활용한 MLOps 시스템 구축

이 프로젝트는 Upbit candle 데이터를 활용하여 MLOps를 위한 workflow를 구현한 프로젝트 입니다.
<br>본 프로젝트는 총 4개의 workflow로 구성되어 있으며 Airflow의 DAG 활용하여 구현 됩니다.
<br>본 프로젝트의 템플릿을 활용하면 별도의 시스템 구축 과정이 불필요 합니다.


## Workflow

<img src="imgs/architecture.jpg" alt='아키텍처' witdh="100%">

1. **Data Workflow**
   - Upbit API를 호출하고 전처리를 수행하는 workflow 입니다.
   - 원천 데이터와 전처리 된 데이터를 각각 별도의 테이블에 저장합니다.
   
2. **Train Workflow**
   - 모델을 학습 및 평가하고 필요시 배포까지 수행하는 workflow 입니다.
   - 학습 기록 및 현재 production 중인 모델은 MLFlow 대시보드에서 조회 할 수 있습니다.
   
3. **Inference Workflow**
   - Production 중인 모델을 활용하여 새로 적재 된 데이터에 대해 예측하는 workflow 입니다.
   - Inference 된 결과와 해당 결과를 통한 모델 성능이 테이블에 저장 되어 tracking 할 수 있습니다.
   
4. **Monitoring Workflow**
   - Inference 결과를 모니터링하는 workflow 입니다.
   - 성능 저하가 감지 되는 경우 re-train 트리거가 작동되어 train workflow를 실행 시킵니다.
   

## 디렉토리 구성

1. **artifacts**
   - MLFlow 활용 시 발생하는 프로젝트 별 실험에 대한 artifact가 저장 되는 폴더 입니다.
   - S3 스토리지 사용시 본 폴더 대신 설정된 Bucket에 저장 됩니다.

2. **compose**
   - Airflow, MLFlow, S3 Storage의 URL 및 credential 정보를 관리합니다.
   - 프로젝트에 대한 config 정보를 관리합니다.
   
3. **dags**
   - Apache Airflow 기반 workflow 파일들로 구성 된 폴더 입니다.
   - 파일명은 <u>*"[프로젝트명]_[구분값]_wf.py"*</u>로 설정 합니다.
   
4. **db_handler**
   - 데이터, workflow의 결과 등 메타 정보들을 처리하기 위한 기능으로 구성 된 폴더 입니다.
   
5. **messenger**
   - Slack 메세징을 위한 기능들로 구성 된 폴더 입니다.
   
6. **service**
   - 모델 관리 및 배포를 위한 기능으로 구성 된 폴더 입니다.
   
7. **crypto_forecast**
   - 주제 별 프로젝트 폴더 입니다.
   - 추가 프로젝트 생성 시 `/root` 디렉토리 내 폴더 생성 후 <u>*"프로젝트 가이드라인"*</u>에 따라 작업을 수행합니다.

  
## 프로젝트 가이드라인

하기 폴더 및 파일들은 필수로 생성 및 작성이 필요합니다.

1. **configs**
   - 데이터, 모델, 하이퍼파라미터 등 설정 값으로 구성 된 파일이 있는 폴더 입니다.
   - class로 구성하며 `/utils.utils.py`의 `load_spec_from_config` 함수에 해당 파일 내 모든 class를 등록합니다.
   
2. **core**
   - Task 단위로 구분된 파일들로 구성 된 폴더 입니다.
   - `/core/load.py`는 `/loader/load.py` 내 함수들을 호출하여 데이터를 불러오는 기능을 수행합니다.
   - `/core/preprocess.py`는 `/preprocessor/data_preparation.py`, `/preprocessor/preprocess.py`, `preprocessor/feature_engineering.py`, `/preprocessor/transformation.py` 내 함수들을 호출하여 데이터를 전처리하는 기능을 수행합니다.
   - `/core/train.py`는 `/trainer/train.py` 내 함수들을 호출하여 모델을 학습하는 기능을 수행합니다.
   - `/core/evaluate.py`는 `/evaluator/evaluate.py` 내 함수들을 호출하여 학습 된 모델을 평가하는 기능을 수행합니다.
   - `/core/inference.py`는 학습 된 모델을 활용하여 새로 적재 된 데이터에 대해 예측을 수행합니다.
   
3. **utils**
   - 프로젝트 내 공통적으로 사용되는 함수들을 작성합니다.
   - `load_spec_from_config` 함수는 필수입니다.

4. **run.py**
   - `/core` 내 각 task들을 호출하여 단계별로 각 과정을 수행하는 실행 파일입니다.
   - config 파일의 파일명을 입력으로 받아 해당 파일에 정의 된 데이터 및 모델을 기반으로 각 task를 수행합니다.
   
5. **주의 사항**
   - `/core`의 각 task에서 호출하는 기능으로 구성 된 파일들은 class 사용을 지양하고 가급적 함수로 작성합니다.
   - 상기 함수들의 경우 동일한 함수명이 중복되지 않게 주의합니다.