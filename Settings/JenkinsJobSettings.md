# GitHub ��
- User -> Setting -> Developer Settings
  - PAT
    - repo �Ƀ`�F�b�N������(���ꂾ����OK)

# Jenkins ��
## Jenkins �S�̂� Credential �ݒ�
- �s�v

## �W���u�ݒ�
- Pipeline script from SCM
  - SCM -> Git
    - URL
      - https://github.com/FourHyphen/Jenkins.git
    - �F��
      - �ǉ�
        - ���[�U�[���p�X���[�h
          - ���[�U�[��: 
          - �p�X���[�h: GitHub �Ŕ��s���� PAT �����
    - �u�����`�w��q
      - */*
    - Script path
      - LoadOtherScript/Tests/AutoTest.groovy
    - Lightweight checkout
      - �`�F�b�N�͓���ĂĂ� OK
      - ���o����O���̂�����炵��

