import argparse
import logging
import os

import sirf.STIR as STIR
from SIRF_data_preparation.data_utilities import (
    prepare_challenge_Siemens_data,
    the_orgdata_path,
)

scanID = 'Siemens_mMR_ACR2'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SyneRBI PETRIC Siemens mMR ACR2 data preparation script.')

    parser.add_argument('--log', type=str, default='warning')
    # disabled these as currenlt not supported
    # parser.add_argument('--start', type=float, default=0)
    # parser.add_argument('--end', type=float, default=500)
    parser.add_argument('--raw_data_path', type=str, default=None)
    args = parser.parse_args()

    if args.log in ['debug', 'info', 'warning', 'error', 'critical']:
        level = eval(f'logging.{args.log.upper()}')
        logging.basicConfig(level=level)
        logging.info(f"Setting logging level to {args.log.upper()}")

    # start = args.start
    # end = args.end

    if args.raw_data_path is None:
        data_path = the_orgdata_path(scanID, 'extracted')
    else:
        data_path = args.raw_data_path

    data_path = os.path.abspath(data_path)
    logging.debug(f"Raw data path: {data_path}")

    intermediate_data_path = the_orgdata_path(scanID, 'processing')
    output_path = the_orgdata_path(scanID, 'fullcounts')

    os.makedirs(output_path, exist_ok=True)
    os.chdir(output_path)
    os.makedirs(intermediate_data_path, exist_ok=True)

    f_template = os.path.join(STIR.get_STIR_examples_dir(), 'Siemens-mMR', 'template_span11.hs')

    prepare_challenge_Siemens_data(data_path, output_path, intermediate_data_path, f_root='', f_listmode='list.l.hdr',
                                   f_mumap='nonexistent', fout_stir_mumap_header='reg_mumap.hv', f_norm='norm.n',
                                   f_template=f_template, start_stop=None)
