SELECT u.id, u.nome, u.email,
		ponto.id, ponto.nome, ponto.cod_ibge_id, loc.municipio
	FROM public.relatorios_usuario as u, public.relatorios_ponto as ponto,
	public.relatorios_ponto_membro as pm, public.relatorios_localizacao as loc
	where u.id = pm.usuario_id and ponto.id = pm.ponto_id
	and ponto.cod_ibge_id = loc.cod_ibge;
	
	
